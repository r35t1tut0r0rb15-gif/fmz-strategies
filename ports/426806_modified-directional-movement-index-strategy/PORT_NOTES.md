# #426806 Modified Directional Movement Index Strategy -> `fmz_426806_modified_dmi`

- Source: https://www.fmz.com/strategy/426806 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 16:41:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [9, 14] x `smoothing` [5, 9]: **4 trials**, defaults 9 / 9 (the source's); MA type EMA.

## Ambiguities resolved

- No na guard: the first bar's na change counts as 0 movement.
- Shorts allowed (default).
- 3-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`
