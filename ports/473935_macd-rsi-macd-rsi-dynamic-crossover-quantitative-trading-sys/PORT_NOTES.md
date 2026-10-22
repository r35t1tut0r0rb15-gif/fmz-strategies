# #473935 MACD-RSI-动态交叉量化交易系统-MACD-RSI-Dynamic-Crossover-Quantitative-Trading-System -> `fmz_473935_macd12_26_9_cross_rsi_filter_long`

- FMZ source id: 473935 (lineage).
- Source: https://www.fmz.com/strategy/473935 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:13:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`overbought` [70, 80] x `oversold` [30, 20]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
