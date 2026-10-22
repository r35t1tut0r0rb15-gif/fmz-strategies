# #490787 Multi Timeframe Dynamic Momentum Wave Capture Strategy -> `fmz_490787_wavetrend_extreme_hourly_ema200_channel_3r_reversal`

- FMZ source id: 490787 (lineage).
- Source: https://www.fmz.com/strategy/490787 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-16 14:53:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; extreme / EMA bracket as fractions of the fill |
| 2 | PASS | WaveTrend extremes with an hourly channel filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity (100 USD) and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rrRatio` [3.0, 1.5] x `overboughtLevel` [50, 60]: **4 trials** (oversold the negative); EMA 12, EMA 200 high / low.

## Ambiguities resolved

- The hourly close is the last completed hour. Repeat-signal re-sends are pending. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend"`.

## Marks

`trailing_stop_pending`
