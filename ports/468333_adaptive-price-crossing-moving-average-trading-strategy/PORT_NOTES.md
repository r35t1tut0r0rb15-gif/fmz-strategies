# #468333 Adaptive Price Crossing Moving Average Trading Strategy -> `fmz_468333_close_cross_hull104_point_bracket_side_flags_reversal`

- FMZ source id: 468333 (lineage).
- Source: https://www.fmz.com/strategy/468333 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:12:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of the fill |
| 2 | PASS | Hull crossings with a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed 2-contract quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_length` [104, 55] x `sl_frac` [0.0000298, 0.01] x `tp_frac` [0.000893, 0.03]: **8 trials**.

## Ambiguities resolved

- Points as fractions of 42000; flags cleared on flat closes (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop`
