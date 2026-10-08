# #366943 AK MACD BB v 1.00 -> `fmz_366943_macd_bollinger_break`

- Source: https://www.fmz.com/strategy/366943 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-31 19:05:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [10, 20] x `dev` [1.0, 1.5, 2.0] = **6 trials**. MACD 12 / 26 stays at the original.

## Ambiguities resolved

- Population stdev; signal length input unused.
- Level tests, so signals repeat while outside; entries reverse.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
