# #490060 多指标交叉动量趋势追踪策略Hull与EMA结合RSI和双重随机震荡器的量化交易系统-Multi-Indicator-Crossover-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Combining-Hull-with-EMA-RSI-and-Dual-Stochastic-Oscillators -> `fmz_490060_hma12_ema5_shift2_cross_rsi_stoch_swing_bracket_reversal`

- FMZ source id: 490060 (lineage).
- Source: https://www.fmz.com/strategy/490060 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-11 11:13:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing bracket as fractions of the fill |
| 2 | PASS | HMA / shifted-EMA crossings with RSI and stochastic filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hmaLength` [12, 20] x `profitFactor` [1.65, 3.0]: **4 trials**; EMA 5 [2], RSI 14, stochs 12 / 5.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
