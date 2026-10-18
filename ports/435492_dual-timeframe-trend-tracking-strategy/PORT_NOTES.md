# #435492 Dual Timeframe Trend Tracking Strategy -> `fmz_435492_ema_trend_and_cross_long`

- FMZ source id: 435492 (lineage).
- Source: https://www.fmz.com/strategy/435492 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 13:46:47). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average trend and cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_short_h` [10, 5] x `len_long_h` [30, 20]: **4 trials**; the EMA 20 / 50 trend pair fixed.

## Ambiguities resolved

- Single chart; close only inside the trend. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
