# #446752 Time Series Adaptive Dynamic Threshold Strategy Based on Equity Data -> `fmz_446752_efficiency_ratio_adaptive_band_long`

- FMZ source id: 446752 (lineage).
- Source: https://www.fmz.com/strategy/446752 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-01 10:48:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the cumulative ratio uses past values only |
| 2 | PASS | Adaptive band breakout and breakdown |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- Ratio measured from the data's first bar. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
