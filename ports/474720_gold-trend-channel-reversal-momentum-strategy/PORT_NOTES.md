# #474720 Gold Trend Channel Reversal Momentum Strategy -> `fmz_474720_trend_engulfing_rsi45_55_atr_stop_point_target_reversal`

- FMZ source id: 474720 (lineage).
- Source: https://www.fmz.com/strategy/474720 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:52:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Trend engulfing candles at a neutral RSI with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- The point target as a fraction of 42000. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
