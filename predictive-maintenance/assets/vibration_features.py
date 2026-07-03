"""Vibration features and envelope analysis for rolling-element bearings.

pip install: numpy scipy
(tested with numpy 2.5, scipy 1.18 on Python 3.14)

Synthetic signal: an outer-race bearing fault produces impulses at the BPFO
(ball-pass frequency, outer race) that excite a structural resonance near
3.2 kHz. The fault energy is tiny next to shaft harmonics and gear mesh, so
the raw spectrum shows nothing at the BPFO; demodulating the resonance band
(band-pass, Hilbert envelope, FFT of the envelope) exposes the BPFO and its
harmonics. This is the standard route to early bearing detection and the
reason band-limited features beat overall RMS for lead time.

Time-domain features included: RMS, kurtosis, crest factor. Kurtosis and
crest factor rise in the early impulsive stage and FALL back toward normal
in late-stage damage as impacts smear together, so a kurtosis that peaks and
then declines while band energy keeps rising signals advanced damage.

Run: python vibration_features.py
"""

from __future__ import annotations

import numpy as np
from scipy import signal

RNG = np.random.default_rng(3)

FS = 25_600.0            # Hz, common CM sample rate
SHAFT_HZ = 25.0          # 1,500 rpm
BPFO_HZ = 3.585 * SHAFT_HZ   # 89.6 Hz for a 6205-style geometry
RESONANCE_HZ = 3_200.0


def make_signal(duration_s: float = 4.0, fault_g: float = 0.0) -> np.ndarray:
    """Baseline machine signature plus an optional outer-race fault.

    Baseline: shaft 1x/2x, gear mesh at 22x shaft with sidebands, broadband
    noise. Fault: impulses at BPFO (with 1% jitter from slip) convolved with
    a decaying resonance at RESONANCE_HZ.
    """
    n = int(duration_s * FS)
    t = np.arange(n) / FS
    x = (0.8 * np.sin(2 * np.pi * SHAFT_HZ * t)
         + 0.4 * np.sin(2 * np.pi * 2 * SHAFT_HZ * t + 1.0)
         + 1.2 * np.sin(2 * np.pi * 22 * SHAFT_HZ * t)
         + 0.3 * np.sin(2 * np.pi * 21 * SHAFT_HZ * t)
         + 0.3 * np.sin(2 * np.pi * 23 * SHAFT_HZ * t)
         + 0.35 * RNG.normal(size=n))
    if fault_g > 0:
        impulse_t = []
        tt = RNG.uniform(0, 1.0 / BPFO_HZ)
        while tt < duration_s:
            impulse_t.append(tt)
            tt += (1.0 / BPFO_HZ) * (1.0 + 0.01 * RNG.normal())
        train = np.zeros(n)
        idx = (np.array(impulse_t) * FS).astype(int)
        train[idx[idx < n]] = fault_g * (1.0 + 0.2 * RNG.normal(size=(idx < n).sum()))
        ring_t = np.arange(int(0.005 * FS)) / FS
        ring = np.exp(-ring_t / 0.0008) * np.sin(2 * np.pi * RESONANCE_HZ * ring_t)
        x = x + signal.fftconvolve(train, ring)[:n]
    return x


def time_features(x: np.ndarray) -> dict[str, float]:
    x = x - x.mean()
    rms = float(np.sqrt(np.mean(x**2)))
    kurt = float(np.mean(x**4) / np.mean(x**2) ** 2)   # unadjusted, normal = 3
    crest = float(np.max(np.abs(x)) / rms)
    return {"rms": rms, "kurtosis": kurt, "crest": crest}


def band_energies(x: np.ndarray, fs: float,
                  bands: list[tuple[float, float]]) -> list[float]:
    f, pxx = signal.welch(x, fs, nperseg=8192)
    return [float(np.trapezoid(pxx[(f >= lo) & (f < hi)],
                               f[(f >= lo) & (f < hi)]))
            for lo, hi in bands]


def pick_demod_band(x: np.ndarray, fs: float, width_hz: float = 800.0
                    ) -> tuple[float, float]:
    """Poor-man's kurtogram: the band whose filtered signal is most impulsive."""
    best, best_k = (0.0, width_hz), -np.inf
    lo = 500.0
    while lo + width_hz <= fs / 2 - 500.0:
        sos = signal.butter(4, [lo, lo + width_hz], "bandpass", fs=fs, output="sos")
        xb = signal.sosfiltfilt(sos, x)
        k = np.mean(xb**4) / np.mean(xb**2) ** 2
        if k > best_k:
            best, best_k = (lo, lo + width_hz), k
        lo += width_hz / 2
    return best


def envelope_spectrum(x: np.ndarray, fs: float, band: tuple[float, float]
                      ) -> tuple[np.ndarray, np.ndarray]:
    sos = signal.butter(4, band, "bandpass", fs=fs, output="sos")
    env = np.abs(signal.hilbert(signal.sosfiltfilt(sos, x)))
    env = env - env.mean()
    spec = np.abs(np.fft.rfft(env)) / len(env)
    freqs = np.fft.rfftfreq(len(env), 1.0 / fs)
    return freqs, spec


def top_peaks(freqs: np.ndarray, spec: np.ndarray, fmax: float, k: int = 5
              ) -> list[tuple[float, float]]:
    m = freqs <= fmax
    f, s = freqs[m], spec[m]
    idx, _ = signal.find_peaks(s, height=0.1 * s.max())
    order = idx[np.argsort(s[idx])[::-1][:k]]
    return [(float(f[i]), float(s[i])) for i in order]


if __name__ == "__main__":
    healthy = make_signal()
    faulty = make_signal(fault_g=1.5)

    print(f"shaft {SHAFT_HZ:.0f} Hz, BPFO {BPFO_HZ:.1f} Hz, "
          f"resonance ~{RESONANCE_HZ:.0f} Hz")
    print(f"{'':<10}{'rms':>8}{'kurtosis':>10}{'crest':>8}"
          f"{'E 2.8-3.6k':>12}{'E 0-1k':>10}")
    bands = [(2_800.0, 3_600.0), (0.0, 1_000.0)]
    for name, x in (("healthy", healthy), ("faulty", faulty)):
        tf = time_features(x)
        eb = band_energies(x, FS, bands)
        print(f"{name:<10}{tf['rms']:>8.3f}{tf['kurtosis']:>10.2f}"
              f"{tf['crest']:>8.2f}{eb[0]:>12.5f}{eb[1]:>10.3f}")

    print("full-band kurtosis stays near 3 because gear and shaft tones"
          " dominate; the impulsiveness only shows once band-limited")

    print("\nraw-spectrum peaks below 400 Hz (faulty) -- BPFO absent:")
    f, pxx = signal.welch(faulty, FS, nperseg=8192)
    for fr, amp in top_peaks(f, pxx, 400.0):
        print(f"  {fr:7.1f} Hz  (shaft x{fr / SHAFT_HZ:.1f})")

    band = pick_demod_band(faulty, FS)
    print(f"\ndemodulation band chosen by kurtosis: "
          f"{band[0]:.0f}-{band[1]:.0f} Hz")
    freqs, spec = envelope_spectrum(faulty, FS, band)
    print("envelope-spectrum peaks below 400 Hz -- BPFO and harmonics:")
    for fr, amp in top_peaks(freqs, spec, 400.0):
        print(f"  {fr:7.1f} Hz  (BPFO x{fr / BPFO_HZ:.2f})")
