# #441057 蜡烛包裹RSI交易策略Engulfing-Candle-RSI-Trading-Strategy -> `fmz_441057_engulfing_after_rsi_extreme_tick_bracket`

- FMZ source id: 441057 (lineage).
- Source: https://www.fmz.com/strategy/441057 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 11:06:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `oversold` [30, 40]: **4 trials**; overbought = 100 - oversold; the ATR multiples fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (0.002 / 0.004 at the daily reading). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
