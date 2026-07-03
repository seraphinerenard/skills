# Sources for the consulting-cases skill

## URL-verified (2026-07-12)

The two researcher fact sheets carry every URL with access dates and
per-source caveats; the curated files in this folder summarize them:

- `research/market-sizing-data-sources.md`: government statistics (StatCan,
  Census, BEA, BLS, FRED, Eurostat), customs and bill-of-lading vendors,
  construction and infrastructure series, company-derived sources,
  alternative-data vendor status, per-capita anchors, and the ready-mixed
  concrete worked example. Summarized in `market-sizing-sources.md`.
- `research/valuation-reference-values.md`: Damodaran and Kroll ERP anchors,
  July 2026 rates, sector WACCs, trading and transaction multiples, control
  premium, DLOM, terminal-growth and mid-year-convention practice, LBO debt
  levels. Summarized in `valuation-anchors.md`.

Both sheets flag their own unverified items (paywalled Kroll size premia,
SaaS Capital exact medians, vendor contract minimums); those flags carry
through to the curated files.

## Cited by name, fetch before quoting page-level detail

- Wong et al., JAMA Internal Medicine 181(8), 2021 (Epic sepsis external
  validation), used in the ML-diligence protocol.
- McKinsey and Bain recurring synergy-realization surveys, used only for
  the directional base rate in `ma-diligence.md`. <!-- allow:C1 synergy is the M&A term of art -->
- US enforcement actions behind the QoE red-flag table; the dedicated M&A
  researcher was cut off before verifying case documents, so
  `ma-diligence.md` names patterns and instructs fetching cases before
  naming parties.

## Repo-internal

- `assets/cohort_engine.py`, `assets/pvm_bridge.py`, `assets/dcf_tornado.py`,
  `assets/mc_sizing.py`: every worked number in SKILL.md marked as a demo
  reproduces from these on synthetic data.
