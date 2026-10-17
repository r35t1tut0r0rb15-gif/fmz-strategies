# #490060 多指标交叉动量趋势追踪策略Hull与EMA结合RSI和双重随机震荡器的量化交易系统-Multi-Indicator-Crossover-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Combining-Hull-with-EMA-RSI-and-Dual-Stochastic-Oscillators -> `fmz_490060_hull_ema_cross_rsi_stoch_swing_bracket`

- FMZ source id: 490060 (lineage).
- Source: https://www.fmz.com/strategy/490060 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-11 11:13:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Moving averages, oscillators and swing levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted (the commission is a cost); the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [12, 20] x `profit_factor` [1.65, 3.0]: **4 trials**; defaults 12 / 1.65 (the source's); EMA 5 [2], RSI 14,
stochastics 12 / 5 (3) and the two-bar stop fixed.

## Ambiguities resolved

- The stop is the lowest low (highest high) of the two bars before the signal bar; a signal whose close is not
  beyond it would be stopped at once on the fill: no entry emitted.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop`
