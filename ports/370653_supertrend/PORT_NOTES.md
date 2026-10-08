# #370653 Supertrend -> `fmz_370653_supertrend_classic`

- Source: https://www.fmz.com/strategy/370653 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-25 09:39:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

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

`period` [7, 10, 14] x `mult` [2.0, 3.0, 4.0] = **9 trials**.

## Ambiguities resolved

- Classic SuperTrend recursion; trend starts 1.
- Same rule as #363807 / #363825 (other defaults / source).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
