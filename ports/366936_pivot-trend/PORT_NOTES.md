# #366936 Pivot Trend -> `fmz_366936_pivot_distance_trend`

- Source: https://www.fmz.com/strategy/366936 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 18:43:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`prd` [3, 4, 6] x `pnum` [3, 5] = **6 trials**.

## Ambiguities resolved

- hrate skips the newest pivot high (loop from i = 1): kept as written.
- Rates are na until all slots are filled; pivots confirmed prd bars later.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
