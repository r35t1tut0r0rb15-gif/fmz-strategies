# #368738 Demark Reversal Points [CC] -> `fmz_368738_demark_reversal_points`

- Source: https://www.fmz.com/strategy/368738 (PineScript v5, author Zer3192, FMZ last
  modified 2022-06-12 17:18:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND361719` (Jaccard 0.65-0.80) with #361719 (PORT_CANDIDATE); best Jaccard 0.670 with #361719. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [6, 9, 13] x `lb_length` [2, 4] = **6 trials**.

## Ambiguities resolved

- Resolution "" = chart (unlike rejected #361719); repainting off reads one bar back ([1]).
- nz() makes missing history 0 (fillna(0) is that nz()).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`.

## Marks (2026-10-07)

`none`
