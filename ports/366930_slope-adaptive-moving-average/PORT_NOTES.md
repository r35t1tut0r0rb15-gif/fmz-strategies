# #366930 Slope Adaptive Moving Average (MZ SAMA) -> `fmz_366930_sama_slope_colour`

- Source: https://www.fmz.com/strategy/366930 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-31 18:24:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [100, 200] x `slope_period` [20, 34] x `flat` [10, 17, 25] = **12 trials**. Major/minor 14/6 and slope range 25 stay at the originals.

## Ambiguities resolved

- Resolution "" = chart. mult is 0 before 201 bars (na test false); the average starts from 0 (nz).
- Slope angle is a ratio of price changes (scale-free).
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks (2026-10-07)

`none`
