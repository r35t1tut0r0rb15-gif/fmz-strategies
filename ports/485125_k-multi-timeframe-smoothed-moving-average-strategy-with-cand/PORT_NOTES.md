# #485125 趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following -> `fmz_485125_candle_reversal_sma200_session`

- FMZ source id: 485125 (lineage).
- Source: https://www.fmz.com/strategy/485125 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 11:02:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle patterns and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/Chicago"] x `len4` [200, 100]: **4 trials**; defaults UTC / 200 (the source as written);
EMA 2 and the 08:30-12:00 window fixed.

## Session open (check 9)

`timestamp(year, month, dayofmonth, 8, 30)` has no time-zone argument, so the window is 08:30-12:00 (inclusive) in
the chart's time zone and the tz input is unused: UTC as written, or America/Chicago (the input's default, DST by
the zone) as the variant. Decision owed: which reading to keep.

## Ambiguities resolved

- "smma" lines are plain SMAs as written. Closes act on the position at the bar's start (#430850). REVERSAL
  INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`none`
