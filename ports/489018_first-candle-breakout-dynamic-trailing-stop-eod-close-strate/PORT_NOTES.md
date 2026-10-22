# #489018 First Candle Breakout Dynamic Trailing Stop EOD Close Strategy -> `fmz_489018_first_candle_0915_breakout_close_trail_1530_close`

- FMZ source id: 489018 (lineage).
- Source: https://www.fmz.com/strategy/489018 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 11:06:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested trail and clock close |
| 2 | PASS | First-candle range breakouts with a range trail |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trailStopMultiplier` [1.5, 3.0] x `endHour` [15, 20]: **4 trials**; first candle 09:15.

## Ambiguities resolved

- The close trail is followed in a loop. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range_breakout"`.

## Marks

`none`
