# #442090 Major Trend Indicator Long -> `fmz_442090_regression_band_trend_state_long`

- FMZ source id: 442090 (lineage).
- Source: https://www.fmz.com/strategy/442090 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 11:15:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression-band states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`linreg_st1` [23, 15] x `linreg_lt` [75, 50]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
