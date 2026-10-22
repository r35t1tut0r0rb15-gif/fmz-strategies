# #439862 Dual Moving Average Breakout Strategy -> `fmz_439862_cdc_action_zone_v2_long`

- FMZ source id: 439862 (lineage).
- Source: https://www.fmz.com/strategy/439862 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 14:49:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings of smoothed ohlc4 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd1` [12, 8] x `prd2` [26, 50]: **4 trials**; EMA 2 smoothing fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
