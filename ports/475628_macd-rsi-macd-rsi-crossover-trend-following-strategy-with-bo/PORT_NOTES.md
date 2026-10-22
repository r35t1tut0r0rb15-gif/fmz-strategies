# #475628 MACD-RSI交叉趋势跟踪策略结合布林带优化系统-MACD-RSI-Crossover-Trend-Following-Strategy-with-Bollinger-Bands-Optimization-System -> `fmz_475628_macd_cross_rsi50_side_long`

- FMZ source id: 475628 (lineage).
- Source: https://www.fmz.com/strategy/475628 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 16:34:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings on the RSI side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7]: **2 trials**; MACD fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
