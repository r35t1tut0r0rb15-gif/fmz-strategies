# #483061 基于唐奇安通道和移动平均线的趋势突破交易策略-Trend-Breakout-Trading-Strategy-Based-on-Donchian-Channel-and-Moving-Average -> `fmz_483061_donchian_expansion_sma200_mid_stop`

- FMZ source id: 483061 (lineage).
- Source: https://www.fmz.com/strategy/483061 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:07:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | Donchian channels and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10] x `stop_frac` [0.45, 0.9]: **4 trials**; defaults 20 / 0.45 (the source's); SMA 200 fixed.

## Trailing stop (mark `trailing_stop_pending`)

Both `strategy.exit` stops run on every bar from the current channel, so they move. The port fixes the signal bar's
distance at entry (re-based on the fill). No target.

## Ambiguities resolved

- A signal whose stop is not beyond the close emits no entry (as #490798). Every bar in the condition is an entry
  signal; a long and a short on one bar: the long is taken (it cannot happen with the SMA filter).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
