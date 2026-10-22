# #484589 双时间框架EMA趋势识别与交易触发量化策略-Dual-Timeframe-EMA-Trend-Recognition-and-Trading-Trigger-Quantitative-Strategy -> `fmz_484589_daily_ema5_30_trend_hourly_ema12_26_cross_swing_stop_reversal`

- FMZ source id: 484589 (lineage).
- Source: https://www.fmz.com/strategy/484589 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 10:28:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing stop as a fraction of the fill |
| 2 | PASS | Hourly EMA crossings in the daily EMA trend |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema_1d` [5, 10] x `short_ema_1h` [12, 9]: **4 trials**; daily EMA 30, hourly EMA 26, 5 % candle trigger, stop over 10 bars.

## Ambiguities resolved

- The daily values are the last completed broker day's. A repeat trigger's re-sent stop is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`trailing_stop_pending`
