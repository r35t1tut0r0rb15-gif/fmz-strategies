# #483106 趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy -> `fmz_483106_rsi14_30_70_cross_adx25_linreg20_side_reversal`

- FMZ source id: 483106 (lineage).
- Source: https://www.fmz.com/strategy/483106 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:46:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crossings with ADX and a regression filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `ml_lookback` [20, 50]: **4 trials**; ADX 14 over 25.

## Ambiguities resolved

- The header's 1h wins over the title's 5min. REVERSAL INTENDED, no other exit. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
