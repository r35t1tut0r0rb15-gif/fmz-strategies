# #435124 Momentum Indicator Driven Trend Following Trading Strategy -> `fmz_435124_unitrend_score_bracket`

- FMZ source id: 435124 (lineage).
- Source: https://www.fmz.com/strategy/435124 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 14:52:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | RSI and average ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital-based quantity, leverage and compounding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_pct` [0.01, 0.03] x `tp_factor` [2.0, 1.0]: **4 trials**; RSI 50 and the 24 / 50 averages fixed.

## Ambiguities resolved

- Change-bar block tracked through the house bracket. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`coarse_bar_stop`
