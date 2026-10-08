# #380525 RSITrend -> `fmz_380525_hull_slope_turn`

- Source: https://www.fmz.com/strategy/380525 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-29 19:57:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

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

`trend_len` [20, 30, 55] = **3 trials**.

## Ambiguities resolved

- Orders use only the Hull slope; the RSI lines only draw.
- ta.hma with round(sqrt(n)).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
