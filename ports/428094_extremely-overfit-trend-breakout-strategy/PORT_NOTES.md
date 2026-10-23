# #428094 Extremely Overfit Trend Breakout Strategy -> `fmz_428094_ema_channel_hull_peaks_trend_volume_obv_filters_flex_stop_flat_only`

- FMZ source id: 428094 (lineage).
- Source: https://www.fmz.com/strategy/428094 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:54:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; volatility-flexed percent stop |
| 2 | PASS | Channel peak / dip entries with trend, volume, ROC and OBV filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission 0.16 %, pyramiding 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`restrictiveness` [-40.0, 0.0] x `stop_loss` [3.0, 5.0]: **4 trials**; channels 6 / 6, Hull 4.

## Ambiguities resolved

- Stop percent fixed at the signal bar; flat follows the house bracket. Volume = broker tick volume.
- FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
