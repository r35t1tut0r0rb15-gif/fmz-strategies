# #437037 Turtle Trading Strategy Based on Simple Moving Average -> `fmz_437037_turtle_fast_channels`

- FMZ source id: 437037 (lineage).
- Source: https://www.fmz.com/strategy/437037 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-29 16:45:51). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_fast` [20, 30] x `exit_fast` [10, 15]: **4 trials**; the slow system is unreachable.

## Ambiguities resolved

- Slow system unreachable (pyramiding 0); call-order fills. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
