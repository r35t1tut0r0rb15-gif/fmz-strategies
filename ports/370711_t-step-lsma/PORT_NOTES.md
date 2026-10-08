# #370711 T-Step LSMA -> `fmz_370711_t_step_lsma`

- Source: https://www.fmz.com/strategy/370711 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-25 16:26:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [50, 100, 200] x `sc` [0.25, 0.5, 0.75] = **9 trials**.

## Ambiguities resolved

- cum()/bar_index is a running mean from the first bar (causal, but data-start dependent), as in Pine.
- b holds until er exists; alpha = corr x sd ratio = regression slope, fixnan when undefined.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks (2026-10-07)

`none`
