# #430775 Hull Moving Average and Kalman Filter Based Trend Tracking Strategy -> `fmz_430775_hull_kalman_cross`

- FMZ source id: 430775 (lineage).
- Source: https://www.fmz.com/strategy/430775 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 17:10:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Smoothed moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [24, 48] x `gain` [10000, 5000]: **4 trials**.

## Ambiguities resolved

- hma3 reads the global length and close, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
