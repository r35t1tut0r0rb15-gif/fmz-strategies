# #489018 首个蜡烛突破-动态追踪止损与收盘平仓策略-First-Candle-Breakout-Dynamic-Trailing-Stop-EOD-Close-Strategy -> `fmz_489018_first_candle_breakout_close_trail_eod`

- FMZ source id: 489018 (lineage).
- Source: https://www.fmz.com/strategy/489018 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 11:06:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked exits |
| 2 | PASS | The first candle's range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "Asia/Kolkata"] x `trail_mult` [1.5, 1.0]: **4 trials**; defaults UTC / 1.5 (the source as
written); the times fixed.

## Session open (check 9)

As #489035: 09:15 first candle, entries from 10:00, close-all at 15:30, in the chart's time zone (UTC on the author's
chart) or Asia/Kolkata (the evident NSE session, no DST). Decision owed: which reading to keep.

## Ambiguities resolved

- The trail is close-checked (no mark). The 15:30 close_all leaves the bar flat; one trade a day.
- REVERSAL INTENDED (only if a trade survived a day). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
