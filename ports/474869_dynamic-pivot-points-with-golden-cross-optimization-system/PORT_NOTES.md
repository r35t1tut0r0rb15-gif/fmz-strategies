# #474869 Dynamic Pivot Points with Golden Cross Optimization System -> `fmz_474869_golden_death_cross_pivot_bar_filter_reversal`

- FMZ source id: 474869 (lineage).
- Source: https://www.fmz.com/strategy/474869 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 16:12:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Golden / death crosses with pivot-bar filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_short` [50, 20] x `length_long` [200, 100]: **4 trials**; pivot length 5.

## Ambiguities resolved

- valuewhen reads the confirmation bar's high / low, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
