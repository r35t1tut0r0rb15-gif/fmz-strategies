# #362870 BRAHMASTRA -> `fmz_362870_brahmastra_kalman_hma_cross`

- Source: https://www.fmz.com/strategy/362870 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-13 15:26:38). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

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

`length` [16, 22, 30] x `gain` [0.5, 0.7, 1.0] = **9 trials**.

## Ambiguities resolved

- Pine v4 integer division: WMA lengths floored (22 -> 11; 11/3 -> 3; 11/2 -> 5).
- Kalman state starts at the first defined input (`nz(kf[1], x)`).
- Trendline module only draws; not ported.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
