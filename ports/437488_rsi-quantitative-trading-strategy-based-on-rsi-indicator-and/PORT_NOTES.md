# #437488 基于RSI指标和包容涨跌形态的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator-and-Engulfing-Pattern -> `fmz_437488_rsi_extreme_engulfing`

- FMZ source id: 437488 (lineage).
- Source: https://www.fmz.com/strategy/437488 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 11:24:08). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and candle comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [9, 14] x `oversold` [25.0, 30.0]: **4 trials**; overbought 60 fixed.

## Ambiguities resolved

- Level-less exits place no order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
