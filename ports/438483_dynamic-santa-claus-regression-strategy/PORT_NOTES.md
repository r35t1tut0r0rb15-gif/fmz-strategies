# #438483 Dynamic Santa Claus Regression Strategy -> `fmz_438483_regression_line_strong_bar_long`

- FMZ source id: 438483 (lineage).
- Source: https://www.fmz.com/strategy/438483 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:00:00). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling regression line and bar shape |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [64, 32, 100, 20]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
