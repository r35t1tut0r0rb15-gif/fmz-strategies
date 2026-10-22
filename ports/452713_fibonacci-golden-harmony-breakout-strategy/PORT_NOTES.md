# #452713 Fibonacci Golden Harmony Breakout Strategy -> `fmz_452713_ema9_21_crossup_close_level_recross_reversal`

- FMZ source id: 452713 (lineage).
- Source: https://www.fmz.com/strategy/452713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 13:56:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Re-crosses of the last cross-up close |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 26]: **4 trials**.

## Ambiguities resolved

- The pocket collapses to the cross-up close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
