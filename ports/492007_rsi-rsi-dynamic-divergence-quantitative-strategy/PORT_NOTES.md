# #492007 RSI动态背离量化策略-RSI-Dynamic-Divergence-Quantitative-Strategy -> `fmz_492007_rsi_divergence_swing_bracket`

- FMZ source id: 492007 (lineage).
- Source: https://www.fmz.com/strategy/492007 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-25 14:57:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after their right bars; the moving bracket fixed at the signal bar (mark). |
| 2 | PASS | RSI divergences, swing levels with a percentage margin, ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`method` ["Swing", "ATR"] x `lb` [5, 3]: **4 trials**; RSI 14, range 5-60, swing 20 bars with a 1 % margin,
ATR 14 x 1.5, reward ratio 2 fixed (the source's).

## Moving bracket (rule 2, mark `trailing_stop_pending`)

As written, `strategy.exit(stop, limit)` is re-issued at every bar's close while in a position, with the stop at the
current 20-bar swing low x 0.99 (or entry - 1.5 x the current ATR) and the target at entry + 2 x (entry - stop): both
move as the window rolls. The house spec has no moving bracket, so the port fixes both at the signal bar:
`sl_stop` = that bar's distance to its swing level (or 1.5 ATR / close), `tp_stop` = 2 x it, shifted one bar inside
`stops()` and re-based on the fill price. Daily bars: `coarse_bar_stop`.

## Ambiguities resolved

- Pivots strict (ties are not pivots), confirmed 5 bars later; "in range" = barssince(pivot)[1] in 5-60.
- Each side's stop distance is taken from the side of that bar's signal.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
