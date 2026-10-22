# #449520 Real time Trendline Trading Based on Pivot Points and Slope -> `fmz_449520_pivot_trendline_atr_slope_break_reversal`

- FMZ source id: 449520 (lineage).
- Source: https://www.fmz.com/strategy/449520 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 15:34:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots used once confirmed |
| 2 | PASS | Sloped trendline breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `mult` [1.0, 2.0]: **4 trials**; the slope method Atr fixed.

## Ambiguities resolved

- Pivots once confirmed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
