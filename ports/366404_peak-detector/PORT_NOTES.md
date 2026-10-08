# #366404 Peak detector -> `fmz_366404_linreg_peak_reversion`

- Source: https://www.fmz.com/strategy/366404 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 09:32:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

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

`length` [50, 100] x `dev` [1.5, 2.0] x `pct` [2.0, 5.0] (both margins) = **8 trials**.

## Ambiguities resolved

- The author's "up"/"down" names are swapped (up is the lower line); orders as coded.
- Same channel as #365345; the 5 % margins are relative.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks (2026-10-07)

`none`
