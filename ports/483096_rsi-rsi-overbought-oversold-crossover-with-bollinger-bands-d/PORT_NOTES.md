# #483096 RSI超买超卖交叉结合布林带动态止盈止损策略-RSI-Overbought-Oversold-Crossover-with-Bollinger-Bands-Dynamic-Stop-Loss-Strategy -> `fmz_483096_rsi14_30_70_cross_swing10_stop_2r_reversal`

- FMZ source id: 483096 (lineage).
- Source: https://www.fmz.com/strategy/483096 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:29:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing bracket as fractions of the fill |
| 2 | PASS | RSI level crossings with swing brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `swing_bars` [10, 20]: **4 trials**; levels 30 / 70, RR 2.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
