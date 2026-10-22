# #483113 Advanced Supertrend Indicator Trading Mechanism Optimization Strategy -> `fmz_483113_supertrend0_25_6_line_cross_on_trend_change_reversal`

- FMZ source id: 483113 (lineage).
- Source: https://www.fmz.com/strategy/483113 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 15:05:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend line crossings on a direction change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`supertrend_length` [6, 10] x `supertrend_factor` [0.25, 1.0]: **4 trials**.

## Ambiguities resolved

- The valuewhen trend-change test is kept as written. REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
