# #474806 Dual BBI Bulls and Bears Index Crossover Strategy -> `fmz_474806_bbi12_80_vs_bbi120_600_cross_long`

- FMZ source id: 474806 (lineage).
- Source: https://www.fmz.com/strategy/474806 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-12 11:16:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | BBI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a_scale` [1.0, 0.5] x `b_scale` [1.0, 0.5]: **4 trials**; each group's four lengths scaled together (rounded), 1.0 = as written.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
