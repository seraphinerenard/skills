# Optimization formulations, derived and worked

Companion to `assets/markdown_dp.py`, `assets/b2b_quote_optimizer.py`, and
`assets/promo_milp.py`. Every number in the worked sections comes from running
those demos with their committed seeds. Sources with URLs live in
`sources.md`.

## The B2B quote first-order condition

The engine prices one deal at a time. Win probability falls in the premium
charged over the deal's reference price r (the market level for that product,
region, and volume band):

```
w(p) = sigmoid(u(p)),   u(p) = a - b * prem(p),   prem(p) = 100 (p/r - 1)
E[margin](p) = w(p) (p - c)
```

Differentiate and set to zero. With `w' = w (1 - w) u'` and `u' = -100 b / r`:

```
0 = w'(p)(p - c) + w(p)
  = -w (1 - w) (100 b / r) (p - c) + w
=> p* - c = r / (100 b (1 - w(p*)))
```

The optimal dollar markup over marginal cost depends on exactly two things:
the local slope of the win curve (b) and the win rate at the optimum. The
customer-value story, the relationship, and the competitive set all act
through a and r; once the curve is fitted they add nothing further to the
markup rule. Because w(p*) sits on the right side, solve by bracketed root
finding on the FOC (the demo uses `brentq`; the profit function is unimodal
for a logistic win curve as long as p > c).

Worked with the demo's committed numbers (r = $100.00, c = $78.00, tier-A
deal so a = 1.0, b = 0.12 per premium point):

```
p*  = $102.71          (grid search over 20,001 points agrees to the cent)
w*  = 0.663
p* - c = $24.71  vs  r / (100 b (1 - w*)) = 100 / (12 * 0.337) = $24.71
E[margin](p*) = $16.37 per unit
```

Two consequences worth quoting in the room:

- Deals you are winning easily (w high, 1 - w small) support a larger
  markup. Uniform "stretch on every deal" guidance has the sign right and
  the shape wrong; the stretch belongs on the deals the curve says you are
  already winning.
- The profit curve is flat near p*. In the demo the band where expected
  margin stays within 95% of its maximum runs from $98.12 to $107.31, which
  is 8.9% of the target price. Hand sales that band as floor / target /
  stretch; keep the point estimate inside the engine. A band survives
  contact with a negotiation; a point price gets overridden and the
  override discredits the engine.

### Endogeneity in the win-curve fit

Historical quote data almost never varies price exogenously: reps cut price
on deals they can see are competitive. Deal competitiveness then lowers both
the quoted premium and the win probability, and the fitted premium
coefficient collapses toward zero or flips positive. The demo constructs
this: true coefficient -0.120, naive fit +0.045 (se 0.007), a clean sign
flip with a confident standard error. Adding a recorded bidder count as a
competitiveness proxy restores -0.107; the remaining gap to -0.120 is proxy
measurement noise. Proxy controls under-correct in proportion to their
noise, so the deployable fix is either an instrument for the quoted premium
or a randomized pricing test on a slice of quotes (see causal-inference for
the test designs). Fit diagnostics that pass on endogenous data are the
trap: the naive fit above has excellent calibration on its own history.

## Markdown as a finite-horizon dynamic program

State (week t, inventory n, ladder step k); actions k' >= k because
markdowns are irreversible in season; demand Poisson with mean
`A_t (p_k / p_0)^beta`; terminal value is salvage.

```
V_t(n, k) = max_{k' >= k}  E_D[ p_{k'} min(D, n) + V_{t+1}(n - min(D, n), k') ]
V_T(n, k) = s * n
```

The DP's edge over a fixed calendar is that it prices the option value of
inventory: with little stock left it holds price to the end; with heavy
stock it drops early while season traffic can still absorb the units. The
demo (16 weeks, 400 units, $60 full price, ladder 60/45/36/24, beta = -2.8,
$8 salvage) gives:

```
DP expected revenue          $18,367   (Monte Carlo check $18,364, se $1.9)
no markdown at all           $13,580   (DP adds 35.2%)
fixed calendar wk 8/12/14    $16,011   (DP adds 14.7%)
```

The policy is a threshold frontier: in week 2 the DP has already marked
down if inventory still exceeds 302 units; by week 8 the threshold is 92.
Merchants read that table directly, which matters for adoption: deliver the
frontier, and the weekly meeting becomes "are we above or below the line"
with no solver in the room.

Two production notes. First, the elasticity that belongs in this DP is the
markdown-range elasticity, estimated from past clearance windows; the
base-price elasticity is smaller and using it under-marks every season.
Second, when demand is unknown at season start, the Caro-Gallien and
Ferreira-Lee-Simchi-Levi deployments both re-estimate the demand rate in
season from early sell-through and re-solve; the DP above is cheap enough
to re-run nightly.

## Promo calendar as a MILP

Binary x[i, w] promotes item i in week w. Own incremental margin m[i, w] is
computed upstream (volume lift at promo price minus discount given to
baseline buyers, scaled by week seasonality). Same-week substitute
cannibalization enters through pair variables:

```
max  sum m[i,w] x[i,w]  -  sum pen[p] y[p,w]
s.t. sum_i x[i,w] <= slots                      (flyer capacity per week)
     sum_w x[i,w] <= max_promos                 (item frequency cap)
     sum_{g=0..G-1} x[i,w+g] <= 1               (min gap, pull-forward guard)
     sum spend[i,w] x[i,w] <= budget
     y[p,w] >= x[i,w] + x[j,w] - 1,  y in [0,1] (pair p = (i, j))
```

Because pen enters the objective as a penalty, the solver pushes every y to
its lower bound, where it equals AND(x_i, x_j); y stays continuous and the
integer count stays at I*W. If any pairwise term were a positive halo
(halo), that pair's y would need the other two AND inequalities
(y <= x_i, y <= x_j) because the solver would otherwise inflate it. Mixed
matrices with both signs take both encodings pair by pair.

Demo result (12 items in 4 substitute triples, 13 weeks, 3 slots, cap 2
promos per item, gap 4, $120k budget, penalty = 55% of the smaller
partner's mean own margin):

```
MILP:    own $78,146   cannibalization $0        net $78,146   (0 clashes)
greedy:  own $78,213   cannibalization -$9,352   net $68,861   (4 clashes)
MILP adds $9,285, +13.5% over margin-ranked greedy
```

The greedy plan actually books slightly more own margin; it gives 12% of it
back in substitute clashes because the top items by margin sit in the same
categories and the same hot weeks. That is the general failure shape:
cannibalization concentrates exactly where naive ranking concentrates.

The cannibalization matrix itself is measured work, owned by
retail-analytics (promo lift decomposition); this MILP consumes it. Keep
the matrix sparse and hierarchical (pairs within category or need-state
only); a dense I x I matrix estimated from one year of weekly data is noise
off the diagonal, and the optimizer will happily arbitrage the noise.

## Capacity-constrained pricing

When a plant or quarry near capacity sells everything it can make, price
stops being a demand lever and becomes an allocation lever. Formally,
maximize `(p - c) v(p)` subject to `v(p) <= K`. At an interior optimum the
standard elasticity rule holds; when the capacity constraint binds with
multiplier lambda, the FOC becomes the same rule with marginal cost
replaced by `c + lambda`, and the optimizer's job collapses to finding the
market-clearing price for K units. The practical reading for aggregates and
building materials: when backlogs run long, every discounted tonne displaces
a full-price tonne, so the true cost of a discount is the full-price margin
forgone. Volume-based capacity planning lives in
supply-chain-optimization; price feeds it the demand curve.
