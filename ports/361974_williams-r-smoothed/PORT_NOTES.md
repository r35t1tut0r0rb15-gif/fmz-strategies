# #361974 Williams-R-Smoothed -> `fmz_361974_smoothed_williams_r_turns`

- Source: https://www.fmz.com/strategy/361974 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 12:08:11). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | %R is dimensionless. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 34, 55] x `fast` [3, 5, 8] = **9 trials**.

## Ambiguities resolved

- Both turn conditions can hold at once between -70 and -30 only if the line is flat-turning; the long line is first in the source.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "williams_r_oscillator"`.

## Marks (2026-10-07)

`none`
