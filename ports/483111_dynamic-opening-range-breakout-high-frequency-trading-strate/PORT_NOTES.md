# #483111 高频动态开盘区间突破交易策略-Dynamic-Opening-Range-Breakout-High-Frequency-Trading-Strategy -> `fmz_483111_ny_orb_midpoint_stop_1600_close`

- FMZ source id: 483111 (lineage).
- Source: https://www.fmz.com/strategy/483111 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 14:02:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop from the signal bar. |
| 2 | PASS | An opening range and a stop inside it. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.5, 1.0] x `last_entry_hour` [12, 11]: **4 trials**; defaults 0.5 / 12 (the source's); the 09:30-09:45
range, the 16:00 close-out and the Tue / Wed / Fri days fixed.

## Target never set (as written)

`limit = strategy.position_avg_price + targetSize` is evaluated on the signal bar, where the position is flat, so the
target is na and never placed (as #489056). Stop only.

## Ambiguities resolved

- Clock (C6): range, entry window and close-out in America/New_York time of the bar's open (DST by the zone);
  `dayofweek(time)` in the chart's zone (UTC on Binance), the same date as New York during the session.
- One trade a day; the 16:00 `close_all` is an exit signal on the 16:00 bar. REVERSAL INTENDED in principle.
- Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range_breakout"`.

## Marks

`none`
