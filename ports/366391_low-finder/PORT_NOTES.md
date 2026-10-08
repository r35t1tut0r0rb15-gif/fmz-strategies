# #366391 Low finder -> `fmz_366391_rsi_extrapolated_extremes`

- Source: https://www.fmz.com/strategy/366391 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 07:41:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [14, 21, 34] = **3 trials**. Levels 0 / 90 stay at the originals.

## Ambiguities resolved

- The "Highdetector" input only toggles plots.
- Levels as coded (0 and 90 on the extrapolated lines).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
