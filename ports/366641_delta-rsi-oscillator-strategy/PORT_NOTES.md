# #366641 Delta-RSI Oscillator Strategy -> `fmz_366641_delta_rsi_zero_cross`

- Source: https://www.fmz.com/strategy/366641 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-30 11:51:02). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`degree` [1, 2, 3] x `rsi_len` [14, 21] x `window` [14, 21] = **12 trials**.

## Ambiguities resolved

- The polynomial-fit slope is a fixed linear filter of the window (weights = d . pinv(J)).
- Default conditions "Zero-Crossing"; RMSE filter off; exit conditions only alert.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
