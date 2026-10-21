# #438950 移动平均线与随机RSI组合交易策略Moving-Average-and-Stochastic-RSI-Combination-Trading-Strategy -> `fmz_438950_stoch_rsi_cross_up_long`

- FMZ source id: 438950 (lineage).
- Source: https://www.fmz.com/strategy/438950 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-16 15:46:11). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | Stochastic RSI crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438950. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_length` [14, 7] x `oversold` [20, 30]: **4 trials**.

## Ambiguities resolved

- Late-armed bracket not ported (trailing_stop_pending); no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
