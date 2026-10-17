# #489035 首个蜡烛突破-止损或收盘自动平仓策略-First-Candle-Breakout-with-Stop-Loss-or-End-of-Day-Closing-Strategy -> `fmz_489035_first_candle_breakout_eod`

- FMZ source id: 489035 (lineage).
- Source: https://www.fmz.com/strategy/489035 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:51:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
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

`session_tz` ["UTC", "Asia/Kolkata"]: **2 trials**; UTC is the source as written on its Binance chart, Asia/Kolkata
the evident NSE session (09:15-15:30, no DST); the times fixed.

## Session open (check 9)

The first candle (09:15), the entry window (from 10:00: "hour > 9") and the close-all (15:30) are clock times in the
chart's time zone; declared per trial by `session_tz`. Decision owed: which reading to keep.

## Ambiguities resolved

- Close-checked range stop (rule 3); the 15:30 close_all leaves the bar flat; one trade a day.
- REVERSAL INTENDED (only if a trade survived a day). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
