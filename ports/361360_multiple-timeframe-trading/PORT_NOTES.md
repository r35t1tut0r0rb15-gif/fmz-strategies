# #361360 跨周期均线交易multiple-timeframe-trading -> `fmz_361360_hourly_vs_daily_ema_side`

- Source: https://www.fmz.com/strategy/361360 (PineScript, FMZ last modified 2022-05-06 16:47:08).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Lower-timeframe request without lookahead: the day's last hourly value at the daily close. |
| 2 | PASS | EMA comparison only. |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ema_length` [3, 5, 10, 20] = **4 trials** (one length for both EMAs, as in the source).

## Ambiguities resolved

- The strategy's bars are daily; the port runs on hourly bars so the hourly EMA is available, and
  trades only at the broker-day close (the daily chart's decision time). `FREQ = "1h"` is the
  module's bar size; the decision cadence is daily (backtest period 1d).
- The comment "5 hour vs 5 days" matches this reading.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks (2026-10-07)

`none`
