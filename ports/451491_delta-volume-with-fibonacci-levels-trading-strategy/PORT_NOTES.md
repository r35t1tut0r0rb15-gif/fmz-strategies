# #451491 Delta Volume with Fibonacci Levels Trading Strategy -> `fmz_451491_candle_colour_range_786_50_levels_long_only`

- FMZ source id: 451491 (lineage).
- Source: https://www.fmz.com/strategy/451491 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 10:45:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour against range retracement levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib_length` [21, 50] x `entry_level` [0.786, 0.618]: **4 trials**; exit level 0.5.

## Ambiguities resolved

- Delta is this bar's only (arrays rebuilt each bar). Volume = sign only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "level_breakout"`.

## Marks

`none`
