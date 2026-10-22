# #442527 MyQuant趋势识别策略MyQuant-Trend-Identifier-Strategy -> `fmz_442527_alma_slope_colour_heat_filter_long`

- FMZ source id: 442527 (lineage).
- Source: https://www.fmz.com/strategy/442527 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 16:04:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ALMA slope / curvature colour states with a heat filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity quantity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alma_len` [140, 70] x `heat_len` [120, 60]: **4 trials**; the colour limits fixed.

## Ambiguities resolved

- One long at a time; ALMA offset as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
