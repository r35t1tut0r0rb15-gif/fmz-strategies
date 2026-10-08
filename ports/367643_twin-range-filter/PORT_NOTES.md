# #367643 Twin Range Filter -> `fmz_367643_twin_range_filter`

- Source: https://www.fmz.com/strategy/367643 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-12 21:00:10). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`per1` [14, 27] x `per2` [55, 100] x `mult2` [2.0, 3.0] = **8 trials**. Fast range 1.6 stays at the original.

## Ambiguities resolved

- Range = mean of the fast and slow smoothed ranges (scale-free).
- Same mechanics as #363562 / #365859.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
