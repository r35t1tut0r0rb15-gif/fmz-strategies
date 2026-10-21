# #436770 Multi factor Quantitative Trading Strategy -> `fmz_436770_reversal123_psy_line_combo`

- FMZ source id: 436770 (lineage).
- Source: https://www.fmz.com/strategy/436770 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 15:46:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns and dimensionless oscillators |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_pline` [20, 12]: **4 trials**; K smoothing 1, D 3 and level 50 fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries sent on every bar; state 0 closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
