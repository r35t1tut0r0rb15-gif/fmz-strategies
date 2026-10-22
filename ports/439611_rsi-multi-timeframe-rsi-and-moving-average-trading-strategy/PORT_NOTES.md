# #439611 基于RSI和平均线的多时间框架交易策略Multi-timeframe-RSI-and-Moving-Average-Trading-Strategy -> `fmz_439611_stoch_rsi_sma5_wma144_swing_bracket`

- FMZ source id: 439611 (lineage).
- Source: https://www.fmz.com/strategy/439611 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 11:00:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing bracket from the signal bar |
| 2 | PASS | Stochastic RSI, averages, swing levels and ATR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [20, 10] x `tp_exp` [30, 15]: **4 trials**; SL expander 10 and the stochastic settings fixed.

## Ambiguities resolved

- Swing bracket from the signal bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
