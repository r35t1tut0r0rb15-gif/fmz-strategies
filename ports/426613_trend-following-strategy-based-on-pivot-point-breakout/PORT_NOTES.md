# #426613 Trend Following Strategy Based on Pivot Point Breakout -> `fmz_426613_pivot_breakout_long`

- Source: https://www.fmz.com/strategy/426613 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 17:20:40). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

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

`left` [5, 10] x `right` [5, 10]: **4 trials**, defaults 10 / 10 (the source's).

## Ambiguities resolved

- Pivots are known on their confirmation bar (right bars later); levels are na until the first pivot.
- Long only.
- 3-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
