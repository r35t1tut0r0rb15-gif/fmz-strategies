# #370655 Gann High Low -> `fmz_370655_gann_hilo_cross`

- Source: https://www.fmz.com/strategy/370655 (PineScript v5, author Zer3192, FMZ last
  modified 2022-06-25 10:00:25). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`h_period` [8, 13, 21] x `l_period` [13, 21, 34] = **9 trials**.

## Ambiguities resolved

- `nz(sma)[1]` is 0 before the SMA exists (fillna(0) here is that nz()), as coded.
- HLv = last non-zero breakout direction.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
