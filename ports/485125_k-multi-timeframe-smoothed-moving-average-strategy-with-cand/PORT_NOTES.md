# #485125 趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following -> `fmz_485125_engulf_3ls_ema2_sma200_side_utc_window_reversal`

- FMZ source id: 485125 (lineage).
- Source: https://www.fmz.com/strategy/485125 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 11:02:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle patterns with a fast / slow average side |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len4` [200, 100] x `ema_fast` [2, 5]: **4 trials**; window 08:30-12:00 UTC.

## Ambiguities resolved

- The window is in UTC (the timezone input is unused, as written). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
