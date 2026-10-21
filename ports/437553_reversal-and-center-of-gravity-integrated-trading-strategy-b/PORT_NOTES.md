# #437553 Reversal and Center of Gravity Integrated Trading Strategy Based on Multi strategy -> `fmz_437553_reversal123_center_of_gravity`

- FMZ source id: 437553 (lineage).
- Source: https://www.fmz.com/strategy/437553 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 16:51:03). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a percent channel around a regression line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_cof` [20, 14] x `length` [14, 28]: **4 trials**; K smoothing 1, D 3, level 50, m 5, 1 % and line 1 fixed; reverse off.

## Ambiguities resolved

- Lengths passed swapped as written; 123 test as written; state 0 closes. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
