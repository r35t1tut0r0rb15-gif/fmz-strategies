# #366385 Super trend B -> `fmz_366385_linreg_band_cross`

- Source: https://www.fmz.com/strategy/366385 (PineScript v5, author Zer3192, FMZ last
  modified 2022-05-29 07:09:06). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`lin_len` [50, 100, 150] x `dev` [1.5, 2.0, 2.5] = **9 trials**.

## Ambiguities resolved

- calcSlope reduces to linreg(close, 150, 0); population stdev.
- The Bollinger SuperTrend lines only alert.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks (2026-10-07)

`none`
