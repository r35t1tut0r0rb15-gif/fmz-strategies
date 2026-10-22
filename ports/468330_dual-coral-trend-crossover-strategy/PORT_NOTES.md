# #468330 Dual Coral Trend Crossover Strategy -> `fmz_468330_coral3_6_cross_no_exit_long`

- FMZ source id: 468330 (lineage).
- Source: https://www.fmz.com/strategy/468330 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:00:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Coral trend crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p1` [3, 5] x `p2` [6, 12]: **4 trials**; the constant 0.2 fixed.

## Ambiguities resolved

- No exit (as written). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
