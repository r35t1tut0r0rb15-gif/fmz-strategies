# #434192 Turtle Breakout Strategy -> `fmz_434192_turtle_close_breakout`

- FMZ source id: 434192 (lineage).
- Source: https://www.fmz.com/strategy/434192 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-04 16:25:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-channel breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_len` [20, 55] x `exit_len` [10, 20]: **4 trials**; the short exit uses exit_len too (10 as written).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
