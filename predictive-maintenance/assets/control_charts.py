"""EWMA and CUSUM drift detection for condition-monitoring trends.

pip install: numpy
(tested with numpy 2.5 on Python 3.14)

Built for slowly drifting health indicators such as spectrometric iron in
oil samples or a vibration band energy. Shewhart +-3 sigma limits catch
step changes and miss slow drift; EWMA and CUSUM trade a small delay on
steps for far earlier drift detection.

Worked constants (Montgomery, Introduction to Statistical Quality Control,
7th ed., ch. 9; verified below by Monte Carlo):
  EWMA  lambda = 0.20, L = 2.859  -> in-control ARL about 370 samples
  CUSUM k = 0.5 sigma, h = 5 sigma -> in-control ARL about 465 samples
  Shewhart 3 sigma                 -> in-control ARL about 370 samples

k = 0.5 sigma tunes CUSUM for a 1 sigma shift (k is half the shift you
want to catch fastest). Both charts assume a stable baseline mean and
sigma estimated from in-control history per component fleet; generic
oil-analysis limit tables ignore fleet-to-fleet baseline differences.

Run: python control_charts.py
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(11)


def ewma_alarm(x: np.ndarray, mu0: float, sigma0: float,
               lam: float = 0.20, L: float = 2.859) -> int:
    """First index where the EWMA leaves its exact time-varying limits.

    Returns -1 if no alarm. Uses the exact variance
    sigma_z(t)^2 = sigma0^2 * lam/(2-lam) * (1 - (1-lam)^(2t)),
    which matters for alarms in the first ~10 samples.
    """
    z = mu0
    for t, xt in enumerate(x, start=1):
        z = lam * xt + (1.0 - lam) * z
        sz = sigma0 * np.sqrt(lam / (2.0 - lam) * (1.0 - (1.0 - lam) ** (2 * t)))
        if abs(z - mu0) > L * sz:
            return t - 1
    return -1


def cusum_alarm(x: np.ndarray, mu0: float, sigma0: float,
                k_sigma: float = 0.5, h_sigma: float = 5.0) -> int:
    """Tabular two-sided CUSUM; first alarming index, -1 if none."""
    k, h = k_sigma * sigma0, h_sigma * sigma0
    hi = lo = 0.0
    for t, xt in enumerate(x):
        hi = max(0.0, hi + (xt - mu0) - k)
        lo = max(0.0, lo + (mu0 - xt) - k)
        if hi > h or lo > h:
            return t
    return -1


def shewhart_alarm(x: np.ndarray, mu0: float, sigma0: float,
                   n_sigma: float = 3.0) -> int:
    hits = np.nonzero(np.abs(x - mu0) > n_sigma * sigma0)[0]
    return int(hits[0]) if hits.size else -1


def monte_carlo_arl(alarm_fn, n_sims: int = 4000, horizon: int = 3000,
                    shift_sigma: float = 0.0) -> float:
    """Average run length under a given standing mean shift.

    Censors runs at the horizon (counts them as horizon), so the
    in-control estimate is a mild underestimate of the true ARL.
    """
    lengths = np.empty(n_sims)
    for s in range(n_sims):
        x = RNG.normal(shift_sigma, 1.0, size=horizon)
        a = alarm_fn(x, 0.0, 1.0)
        lengths[s] = horizon if a < 0 else a + 1
    return float(lengths.mean())


def drift_demo() -> None:
    """Oil-analysis iron: baseline 18 ppm sigma 4, drift +0.15 ppm/sample."""
    mu0, sigma0 = 18.0, 4.0
    n_baseline, n_total, drift = 60, 220, 0.15
    x = RNG.normal(mu0, sigma0, size=n_total)
    ramp = np.maximum(0, np.arange(n_total) - n_baseline) * drift
    x = x + ramp

    print(f"iron ppm, drift starts at sample {n_baseline} "
          f"(+{drift} ppm/sample, {drift / sigma0:.3f} sigma/sample)")
    for name, fn in (("Shewhart 3s", shewhart_alarm),
                     ("EWMA(0.2, 2.859)", ewma_alarm),
                     ("CUSUM(0.5s, 5s)", cusum_alarm)):
        a = fn(x, mu0, sigma0)
        if a < 0:
            print(f"  {name:<18} no alarm in {n_total} samples")
        else:
            lag = a - n_baseline
            level = mu0 + max(0, a - n_baseline) * drift
            print(f"  {name:<18} alarm at sample {a} "
                  f"({lag:+d} vs drift onset, true mean {level:.1f} ppm)")


if __name__ == "__main__":
    print("=== in-control ARL check (Monte Carlo, 4,000 runs) ===")
    for name, fn, published in (("Shewhart 3s", shewhart_alarm, 370.0),
                                ("EWMA(0.2, 2.859)", ewma_alarm, 370.0),
                                ("CUSUM(0.5s, 5s)", cusum_alarm, 465.0)):
        arl0 = monte_carlo_arl(fn)
        print(f"  {name:<18} ARL0 = {arl0:6.0f}  (published ~{published:.0f})")

    print("\n=== out-of-control ARL, standing 1 sigma shift ===")
    for name, fn in (("Shewhart 3s", shewhart_alarm),
                     ("EWMA(0.2, 2.859)", ewma_alarm),
                     ("CUSUM(0.5s, 5s)", cusum_alarm)):
        arl1 = monte_carlo_arl(fn, shift_sigma=1.0)
        print(f"  {name:<18} ARL1 = {arl1:6.1f} samples")

    print("\n=== slow-drift detection demo ===")
    drift_demo()
