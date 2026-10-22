# #449957 Pivot-and-Momentum-Strategy-枢轴动量策略 -> `fmz_449957_hourly_pivot_side_stochrsi_cross_roc_reversal`

- FMZ source id: 449957 (lineage).
- Source: https://www.fmz.com/strategy/449957 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:39:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the hourly values end with the daily bar |
| 2 | PASS | Stochastic-RSI crossings with a pivot side and ROC sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [9, 14] x `stoch_len` [14, 9]: **4 trials**; the smoothing and the RSI length fixed.

## Ambiguities resolved

- Pivot from the day's second-last hourly bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
