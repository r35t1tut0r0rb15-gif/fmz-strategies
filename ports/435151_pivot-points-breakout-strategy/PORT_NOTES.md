# #435151 Pivot Points Breakout Strategy -> `fmz_435151_floor_pivot_r1_s1_side`

- FMZ source id: 435151 (lineage).
- Source: https://www.fmz.com/strategy/435151 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 16:47:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Prior-day pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True]: **2 trials**.

## Ambiguities resolved

- Previous broker day's pivots. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
