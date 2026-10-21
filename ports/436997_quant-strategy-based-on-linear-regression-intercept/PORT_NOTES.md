# #436997 Quant Strategy Based on Linear Regression Intercept -> `fmz_436997_linreg_intercept_side_state`

- FMZ source id: 436997 (lineage).
- Source: https://www.fmz.com/strategy/436997 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-29 11:45:20). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against a regression line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28]: **2 trials**; reverse off.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
