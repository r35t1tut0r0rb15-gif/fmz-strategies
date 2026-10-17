# #435152 Center of Gravity Backtesting Trading Strategy -> `fmz_435152_center_of_gravity_bands`

- FMZ source id: 435152 (lineage).
- Source: https://www.fmz.com/strategy/435152 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 16:56:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A regression line with percent bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `percent` [1.0, 0.5]: **4 trials**; offset 5 and line 1 fixed.

## Ambiguities resolved

- Pine linreg offset convention. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
