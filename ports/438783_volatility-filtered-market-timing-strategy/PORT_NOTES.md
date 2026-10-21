# #438783 Volatility Filtered Market Timing Strategy -> `fmz_438783_hold_outside_volatility_extremes`

- FMZ source id: 438783 (lineage).
- Source: https://www.fmz.com/strategy/438783 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 12:27:47). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Historical volatility percentile |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital and percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`upper` [95, 90, 80, 99]: **4 trials**; HV 10 and the 100-bar window fixed.

## Ambiguities resolved

- Lookback input has no effect; held while the percentile is undefined. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
