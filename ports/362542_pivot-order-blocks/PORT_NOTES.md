# #362542 Pivot-Order-Blocks -> `fmz_362542_pivot_side_10`

- Source: https://www.fmz.com/strategy/362542 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 23:35:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

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

`left` [5, 10, 20] x `right` [5, 10] = **6 trials**.

## Ambiguities resolved

- Same rule as #361802 (pivot low long, pivot high short) with 10/10 pivots and if/else-if (pivot low wins a tie); near, not exact.
- No backtest header: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`bar_size_pending`
