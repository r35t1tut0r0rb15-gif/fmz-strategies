# #437377 Combo Trend Tracking Strategy -> `fmz_437377_reversal123_dti_combo`

- FMZ source id: 437377 (lineage).
- Source: https://www.fmz.com/strategy/437377 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-02 10:41:30). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a dimensionless trend index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `r` [14, 25]: **4 trials**; K smoothing 1, D 3, level 50, s 10, u 5 and the +-45 levels fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
