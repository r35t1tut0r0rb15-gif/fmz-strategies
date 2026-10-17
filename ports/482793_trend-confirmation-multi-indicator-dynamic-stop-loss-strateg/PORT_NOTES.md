# #482793 基于趋势确认的多重指标动态止损策略-Trend-Confirmation-Multi-Indicator-Dynamic-Stop-Loss-Strategy -> `fmz_482793_sma_macd_adx_long_swing_low_stop`

- FMZ source id: 482793 (lineage).
- Source: https://www.fmz.com/strategy/482793 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 11:19:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late swing-low stop as an exit signal (marked). |
| 2 | PASS | An SMA, MACD, ADX and swing lows. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [30, 50] x `adx_min` [25, 20]: **4 trials**; defaults 30 / 25 (the source's); MACD 9 / 18 / 9 and DMI /
ADX 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit(stop = secondLastSwingLow)` is placed only once the close is under the SMA and two swing lows have
been recorded during the trade, and is replaced while that holds, so the level appears after the entry and moves.
The house bracket is fixed at the fill and cannot carry it. `simulate()` keeps the resting order bar by bar and
emits an exit signal on the bar whose low reaches the level (filled at the next open, one bar after Pine's stop
fill); a level placed at or above the close exits at the next open, as Pine's stop would.

## Ambiguities resolved

- `lastSwingLow := low[1]` on the bar after the swing is confirmed records the bar after the swing low (as written).
- The swing lows are forgotten on every bar without a position, as written.
- No entry is emitted on a bar where the stop is reached (Pine could re-enter there).
- Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`trailing_stop_pending`
