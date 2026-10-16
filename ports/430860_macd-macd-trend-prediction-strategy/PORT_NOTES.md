# #430860 MACD趋势预测策略MACD-Trend-Prediction-Strategy -> `fmz_430860_zero_lag_macd_long`

- FMZ source id: 430860 (lineage).
- Source: https://www.fmz.com/strategy/430860 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 15:25:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Zero-lag moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
