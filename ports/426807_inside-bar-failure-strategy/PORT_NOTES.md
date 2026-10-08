# #426807 Inside Bar Failure Strategy -> `fmz_426807_inside_bar_failure`

- Source: https://www.fmz.com/strategy/426807 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 16:43:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

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

`forward` [2, 3, 5]: **3 trials**, default 3 (the source's).

## Ambiguities resolved

- Fills in issue order: a reversing entry stands; a refused same-side entry plus that side's timed close goes flat.
- 4-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
