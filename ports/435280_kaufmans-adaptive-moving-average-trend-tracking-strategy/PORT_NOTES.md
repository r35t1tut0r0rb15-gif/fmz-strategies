# #435280 Kaufmans Adaptive Moving Average Trend Tracking Strategy -> `fmz_435280_kama_trend_follow`

- FMZ source id: 435280 (lineage).
- Source: https://www.fmz.com/strategy/435280 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-13 17:25:33). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot and pyramiding input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 10] x `type` ["Trend", "Crossing"]: **4 trials**; fast 2 and slow 30 fixed.

## Ambiguities resolved

- KAMA start from zero as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
