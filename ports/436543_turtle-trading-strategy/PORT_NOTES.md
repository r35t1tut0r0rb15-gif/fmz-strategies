# #436543 Turtle Trading Strategy -> `fmz_436543_turtle_fast_channel`

- FMZ source id: 436543 (lineage).
- Source: https://www.fmz.com/strategy/436543 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 17:12:05). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_fast` [20, 30] x `exit_fast` [10, 15]: **4 trials**; the dead slow system is not searched.

## Ambiguities resolved

- Slow entries unreachable, left out. Fills at the next open, not at the channel. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
