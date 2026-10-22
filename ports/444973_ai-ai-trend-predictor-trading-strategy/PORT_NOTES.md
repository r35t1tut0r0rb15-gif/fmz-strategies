# #444973 AI趋势预测交易策略AI-Trend-Predictor-Trading-Strategy -> `fmz_444973_sma192_cross_range_autocorr_filter_reversal`

- FMZ source id: 444973 (lineage).
- Source: https://www.fmz.com/strategy/444973 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 16:06:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the "future" close is a past value and only plots |
| 2 | PASS | SMA crossings with an autocorrelation filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_b` [192, 100] x `length_c` [10, 20]: **4 trials**; the 0.51 level fixed.

## Ambiguities resolved

- Undefined correlation counts as not positive. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
