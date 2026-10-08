# #366966 Fibonacci Timing Pattern -> `fmz_366966_fibonacci_timing_pattern`

- Source: https://www.fmz.com/strategy/366966 (PineScript v5, author Zer3192, FMZ last
  modified 2022-05-31 21:25:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameters: **1 trial**, the source as written.

## Ambiguities resolved

- `FB_Buy == false` inside the if is a comparison (no effect).
- Pattern fixed in the source.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`.

## Marks (2026-10-07)

`none`
