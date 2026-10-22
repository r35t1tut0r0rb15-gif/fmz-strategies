# #439972 Kalman Filter Based Trend Tracking Strategy -> `fmz_439972_kalman_slope_angle_sum`

- FMZ source id: 439972 (lineage).
- Source: https://www.fmz.com/strategy/439972 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 14:12:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 1-minute value is the bar close |
| 2 | ADAPT | Price-scale slope angle -> angle of the slope on a BTC scale |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439972. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`scale` [42000.0, 4200.0] x `period` [30, 15]: **4 trials**; gain 0.01 and +/- 360 fixed.

## Ambiguities resolved

- Slope angle read on a BTC scale. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
