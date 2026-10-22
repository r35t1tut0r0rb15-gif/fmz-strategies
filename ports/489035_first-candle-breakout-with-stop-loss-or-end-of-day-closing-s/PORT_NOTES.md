# #489035 First Candle Breakout with Stop Loss or End of Day Closing Strategy -> `fmz_489035_first_candle_0915_breakout_range_stop_1530_close`

- FMZ source id: 489035 (lineage).
- Source: https://www.fmz.com/strategy/489035 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:51:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested stop and clock close |
| 2 | PASS | First-candle range breakouts |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`startHour` [9, 13] x `endHour` [15, 20]: **4 trials**; first candle at minute 15, close at minute 30.

## Ambiguities resolved

- Close-tested stops in a loop. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range_breakout"`.

## Marks

`none`
