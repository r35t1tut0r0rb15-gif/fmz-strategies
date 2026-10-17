# #489010 多层级布林带趋势跟踪与反转交易策略-Multi-level-Bollinger-Bands-Trend-Following-and-Reversal-Trading-Strategy -> `fmz_489010_bb_reentry_bar_count_exits_6d`

- FMZ source id: 489010 (lineage).
- Source: https://www.fmz.com/strategy/489010 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:16:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked exits; the trail pending (mark). |
| 2 | PASS | Band positions and bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the trail quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`x_bars` [3, 2] x `y_bars` [10, 5]: **4 trials**; defaults 3 / 10 (the source's); BB 20 x 2 fixed.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, every bar in a trade: `strategy.exit(trail_price = entry + 2 x (entry - lower), trail_offset =
(entry - lower) x (1 - 30 %))` (shorts mirrored with the upper band). The activation and offset depend on the
current band distance (moving, per trade); `trail_offset` takes ticks but gets a price distance (read as a price
distance, #427592). Not expressible in the house trail: not emitted.

## Ambiguities resolved

- Bar-count exits close-checked (rule 3), from the position held at the bar's start; counters reset only when flat.
- Both signals on one bar: the short wins. REVERSAL INTENDED.
- Six-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
