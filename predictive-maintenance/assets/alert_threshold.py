"""Cost-optimal alert thresholds and capacity-constrained ranking.

pip install: numpy
(tested with numpy 2.5 on Python 3.14)

Setting the alert threshold is an economics problem, and the numbers say
alert far below 50% probability. For a calibrated weekly failure
probability p, alerting pays when

    p > c_inspection / (c_unplanned - c_planned)

because an alert always buys an inspection, and with probability p it
converts an unplanned failure into a planned repair. Worked numbers for a
haul-truck final drive:

    c_inspection = $1,800    (technician, oil sample, downtime slot)
    c_planned    = $95,000   (scheduled change-out)
    c_unplanned  = $260,000  (failure in service: tow, consequential
                              damage, extra downtime at ~$8k/h)
    p* = 1,800 / 165,000 = 1.09%

The demo below checks this against empirical cost minimization, shows the
cost of applying the formula to MISCALIBRATED scores (the usual state of a
fresh model), and sizes alerts to planner capacity with precision-at-k.

Run: python alert_threshold.py
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(21)

C_INSPECT = 1_800.0
C_PLANNED = 95_000.0
C_UNPLANNED = 260_000.0


def closed_form_threshold() -> float:
    return C_INSPECT / (C_UNPLANNED - C_PLANNED)


def weekly_cost(p_hat: np.ndarray, y: np.ndarray, thr: float) -> float:
    """Expected realized cost per asset-week for a threshold policy.

    Alert: inspection always; planned repair if truly failing.
    No alert: unplanned failure cost if truly failing.
    """
    alert = p_hat >= thr
    cost = np.where(alert,
                    C_INSPECT + y * C_PLANNED,
                    y * C_UNPLANNED)
    return float(cost.mean())


def simulate_scores(n: int = 200_000, temper: float = 1.0
                    ) -> tuple[np.ndarray, np.ndarray]:
    """Asset-weeks with true labels and model scores.

    True weekly risk is drawn per asset-week and labels are Bernoulli in
    that risk, so the untempered score is calibrated by construction.
    temper > 1 applies a monotone logit distortion: identical ranking,
    overconfident probabilities, the common state of a model trained on
    rebalanced data.
    """
    logit_p = RNG.normal(-5.8, 1.3, n)
    p_true = 1.0 / (1.0 + np.exp(-logit_p))
    y = (RNG.random(n) < p_true).astype(float)
    p_hat = 1.0 / (1.0 + np.exp(-(temper * logit_p + 2.5 * (temper - 1.0))))
    return p_hat, y


def sweep_threshold(p_hat: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    grid = np.geomspace(1e-4, 0.5, 200)
    costs = [weekly_cost(p_hat, y, t) for t in grid]
    i = int(np.argmin(costs))
    return float(grid[i]), float(costs[i])


def precision_at_k(p_hat: np.ndarray, y: np.ndarray, fleet: int, k: int
                   ) -> tuple[float, float]:
    """Weekly top-k policy: precision and expected saving per inspection.

    Draws fleet-sized weeks from the pool and ranks within each week,
    matching how a planner consumes the model (k inspection slots/week).
    """
    n_weeks = len(p_hat) // fleet
    hits = total = 0
    for w in range(n_weeks):
        sl = slice(w * fleet, (w + 1) * fleet)
        order = np.argsort(p_hat[sl])[::-1][:k]
        hits += int(y[sl][order].sum())
        total += k
    prec = hits / total
    saving = prec * (C_UNPLANNED - C_PLANNED) - C_INSPECT
    return prec, saving


if __name__ == "__main__":
    p_star = closed_form_threshold()
    print(f"closed-form threshold p* = {p_star:.4f} "
          f"({p_star:.2%}, far below 0.5)")

    print("\n=== calibrated scores ===")
    p_hat, y = simulate_scores(temper=1.0)
    t_emp, c_emp = sweep_threshold(p_hat, y)
    print(f"base rate {y.mean():.3%}; empirical optimum {t_emp:.4f} "
          f"(cost ${c_emp:,.0f}/asset-week) vs p* {p_star:.4f} "
          f"(cost ${weekly_cost(p_hat, y, p_star):,.0f})")
    print(f"never-alert cost ${weekly_cost(p_hat, y, 1.1):,.0f}, "
          f"alert-everyone cost ${weekly_cost(p_hat, y, 0.0):,.0f}")

    print("\n=== overconfident scores, same ranking skill ===")
    p_hat_m, y_m = simulate_scores(temper=2.0)
    t_emp_m, c_emp_m = sweep_threshold(p_hat_m, y_m)
    c_formula = weekly_cost(p_hat_m, y_m, p_star)
    print(f"p* on miscalibrated scores costs ${c_formula:,.0f}/asset-week; "
          f"empirical threshold {t_emp_m:.4f} costs ${c_emp_m:,.0f} "
          f"(gap ${c_formula - c_emp_m:,.0f}/asset-week across the fleet)")
    print("recalibrate (isotonic/Platt on a held-out fold) or pick the "
          "threshold empirically on validation weeks; never trust p* "
          "against raw scores from a rebalanced training set")

    print("\n=== planner capacity: fleet of 120, k slots/week ===")
    print(f"{'k':>4}{'precision':>11}{'net $/inspection':>18}")
    for k in (2, 4, 6, 10, 20):
        prec, save = precision_at_k(p_hat, y, fleet=120, k=k)
        print(f"{k:>4}{prec:>11.2%}{save:>18,.0f}")
    print("expand k while the marginal inspection still nets out positive "
          "and the planners can absorb it; k is a budget, p* is a bound")
