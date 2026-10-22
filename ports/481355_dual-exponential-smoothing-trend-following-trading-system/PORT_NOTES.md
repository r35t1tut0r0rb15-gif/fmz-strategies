# #481355 Dual Exponential Smoothing Trend Following Trading System -> `fmz_481355_weighted_avg9_30_cross_point_bracket_reversal`

- FMZ source id: 481355 (lineage).
- Source: https://www.fmz.com/strategy/481355 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:46:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; point bracket as fractions of the fill |
| 2 | PASS | Weighted-average crossings with a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`primary` [9, 5] x `secondary` [30, 60]: **4 trials**; target / stop 30 points (fractions of 42000).

## Ambiguities resolved

- The 30 points are price amounts (fractions of 42000). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
