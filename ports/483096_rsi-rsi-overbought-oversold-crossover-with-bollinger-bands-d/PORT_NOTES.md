# #483096 RSI超买超卖交叉结合布林带动态止盈止损策略-RSI-Overbought-Oversold-Crossover-with-Bollinger-Bands-Dynamic-Stop-Loss-Strategy -> `fmz_483096_rsi_exit_extreme_swing_stop_2r`

- FMZ source id: 483096 (lineage).
- Source: https://www.fmz.com/strategy/483096 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:29:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | RSI and rolling swing extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 3.0] x `swing_len` [10, 20]: **4 trials**; defaults 2 / 10 (the source's); RSI 14 (30 / 70) fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- The swing stop and 2 R target become fractions of the signal close by side, re-based on the fill; a signal whose
  stop is not beyond the close emits no entry (as #490798). The Bollinger bands of the title only feed plots.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
