"""Event-based evaluation for failure-prediction models.

pip install: numpy
(tested with numpy 2.5 on Python 3.14)

Point-wise metrics (daily precision/recall/F1 on window labels) inflate
apparent performance: one detected failure with a sticky alarm contributes
dozens of true-positive days, while an undetected failure contributes a
few false-negative days. The unit of value is the EVENT: a failure either
got an actionable warning or it did not.

Rules implemented here:
  - A failure counts as detected only if an alarm fires inside its
    actionable window [t_f - w_max, t_f - w_min]. Alarms closer than
    w_min give planners no time to act; alarms further out than w_max
    are indistinguishable from noise.
  - Consecutive alarm days collapse into one alarm EPISODE; precision is
    computed over episodes so a latched alarm cannot vote for itself.
  - Machines that never fail still contribute exposure time, which is
    what false-alarms-per-machine-year needs (evaluation under censoring).
  - Lead time = days from first in-window alarm to failure; report the
    distribution, since the mean hides the too-late mass.

Run: python event_evaluation.py
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(5)

W_MIN, W_MAX = 3, 30          # actionable window, days before failure


def episodes(alarm: np.ndarray) -> list[tuple[int, int]]:
    """Consecutive alarm days -> [(start, end)] inclusive."""
    days = np.nonzero(alarm)[0]
    if days.size == 0:
        return []
    out, start, prev = [], days[0], days[0]
    for d in days[1:]:
        if d > prev + 1:
            out.append((start, prev))
            start = d
        prev = d
    out.append((start, prev))
    return out


def evaluate_fleet(alarms: list[np.ndarray], failures: list[list[int]],
                   w_min: int = W_MIN, w_max: int = W_MAX) -> dict:
    """Event-based metrics over a fleet of daily alarm vectors."""
    n_events = detected = late_only = 0
    good_ep = false_ep = total_ep = 0
    lead_times: list[int] = []
    exposure_days = 0

    for alarm, fails in zip(alarms, failures):
        exposure_days += len(alarm)
        eps = episodes(alarm)
        total_ep += len(eps)
        windows = [(max(0, f - w_max), f - w_min, f) for f in fails]

        for lo, hi, f in windows:
            n_events += 1
            in_win = [d for s, e in eps for d in range(s, e + 1) if lo <= d <= hi]
            if in_win:
                detected += 1
                lead_times.append(f - min(in_win))
            elif any(hi < d <= f for s, e in eps for d in range(s, e + 1)):
                late_only += 1

        for s, e in eps:
            days = range(s, e + 1)
            if any(lo <= d <= hi for lo, hi, _ in windows for d in days):
                good_ep += 1
            elif any(hi < d <= f for _, hi, f in windows for d in days):
                pass                      # late: neither credited nor penalized
            else:
                false_ep += 1

    lt = np.array(lead_times) if lead_times else np.array([np.nan])
    return {
        "event_recall": detected / n_events,
        "late_only_rate": late_only / n_events,
        "episode_precision": good_ep / total_ep if total_ep else float("nan"),
        "false_per_machine_year": false_ep / (exposure_days / 365.0),
        "lead_p25": float(np.percentile(lt, 25)),
        "lead_median": float(np.percentile(lt, 50)),
        "lead_p75": float(np.percentile(lt, 75)),
        "n_events": n_events,
    }


def pointwise_prf(alarms: list[np.ndarray], failures: list[list[int]],
                  w_min: int = W_MIN, w_max: int = W_MAX
                  ) -> tuple[float, float, float]:
    tp = fp = fn = 0
    for alarm, fails in zip(alarms, failures):
        label = np.zeros_like(alarm)
        for f in fails:
            label[max(0, f - w_max): max(0, f - w_min) + 1] = 1
        tp += int(((alarm == 1) & (label == 1)).sum())
        fp += int(((alarm == 1) & (label == 0)).sum())
        fn += int(((alarm == 0) & (label == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return prec, rec, f1


def simulate_fleet(n_machines: int = 60, horizon_d: int = 1095
                   ) -> tuple[list[np.ndarray], list[list[int]]]:
    """Failures at ~0.6/yr; 70% give a detectable ramp, 30% are sudden.

    The alarm latches once the (noisy) degradation score crosses its
    threshold, and random spikes create false episodes, mimicking a real
    anomaly detector on a fleet.
    """
    alarms, failures = [], []
    for _ in range(n_machines):
        fails, t = [], 0
        while True:
            t += int(RNG.exponential(365 / 0.6)) + 30
            if t >= horizon_d:
                break
            fails.append(t)
        alarm = np.zeros(horizon_d, dtype=int)
        for f in fails:
            if RNG.random() < 0.70:               # detectable degradation
                onset = f - int(np.clip(RNG.lognormal(2.6, 0.6), 4, 60))
                ramp_len = f - max(onset, 0)
                if ramp_len > 0:
                    prog = np.linspace(0, 1, ramp_len) + RNG.normal(0, 0.25, ramp_len)
                    first = np.nonzero(prog > 0.55)[0]
                    if first.size:
                        alarm[max(onset, 0) + first[0]: f + 1] = 1
        n_spikes = RNG.poisson(2.0 * horizon_d / 365)
        for s in RNG.integers(0, horizon_d, n_spikes):
            alarm[s: s + RNG.integers(1, 4)] = 1
        alarms.append(alarm)
        failures.append(fails)
    return alarms, failures


if __name__ == "__main__":
    alarms, failures = simulate_fleet()
    prec, rec, f1 = pointwise_prf(alarms, failures)
    ev = evaluate_fleet(alarms, failures)

    print(f"fleet: {len(alarms)} machines x 3 y, {ev['n_events']} failures, "
          f"window {W_MIN}-{W_MAX} d before failure")
    print(f"\npoint-wise  precision {prec:.2f}  recall {rec:.2f}  F1 {f1:.2f}")
    print(f"event-based recall {ev['event_recall']:.2f}  "
          f"episode precision {ev['episode_precision']:.2f}  "
          f"false alarms {ev['false_per_machine_year']:.1f}/machine-year")
    print(f"lead time p25/median/p75 = {ev['lead_p25']:.0f}/"
          f"{ev['lead_median']:.0f}/{ev['lead_p75']:.0f} d; "
          f"detected too late (inside {W_MIN} d): {ev['late_only_rate']:.0%}")
    print("\npoint-wise precision doubles the episode precision because a "
          "latched alarm votes for itself once per day, and point-wise "
          "recall hides that most failures did get an actionable warning; "
          "report event recall, episode precision, false alarms per "
          "machine-year, and the lead-time distribution")
