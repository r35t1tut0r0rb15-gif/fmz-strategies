# #483080 Adaptive Bollinger Bands Grid Trading Strategy with Dynamic Level Adjustment -> `fmz_483080_bb20_2_grid4_1pct_level_cross_reversal`

- FMZ source id: 483080 (lineage).
- Source: https://www.fmz.com/strategy/483080 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:04:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent grid levels off the Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`grid_distance_percent` [1.0, 2.0] x `length` [20, 40]: **4 trials**; band 2 sd, 4 levels.

## Ambiguities resolved

- Grid adds are refused by default pyramiding. REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
