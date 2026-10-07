# #365078 ATR Smoothed (By dysrupt)_BuySell version -> `fmz_365078_atr_trailing_stop_flip`

- Source: https://www.fmz.com/strategy/365078 (PineScript v3, author ChaoZhang, FMZ last
  modified 2022-05-23 14:12:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`atr_period` [14, 21, 28] x `mult` [3.0, 4.5, 6.3] = **9 trials**.

## Ambiguities resolved

- isLong/isShort latches make LONG/SHORT the first bar of a new pos (always-in reversal).
- VWMA smooth line (volume) only draws: no volume used.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
