# #484589 双时间框架EMA趋势识别与交易触发量化策略-Dual-Timeframe-EMA-Trend-Recognition-and-Trading-Trigger-Quantitative-Strategy -> `fmz_484589_daily_ema_trend_hourly_cross_stop`

- FMZ source id: 484589 (lineage).
- Source: https://www.fmz.com/strategy/484589 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 10:28:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop from the signal bar (re-placement marked). |
| 2 | PASS | EMAs, a percentage move and rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`d_short` [5, 10] x `move_pct` [5.0, 3.0]: **4 trials**; defaults 5 / 5 (the source's); daily EMA 30, hourly EMA
12 / 26 and the 10-bar extremes fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop at the new bar's 10-bar extreme (its `strategy.exit`). The port
keeps the entry's stop.

## Ambiguities resolved

- The daily EMAs (`request.security("1D")`) are the last completed broker day's (house rule, as #430771); the
  "60" security on the 1-hour chart is the bar's own value. A signal whose stop is not beyond the close (zero
  distance) emits no entry (as #491035). Both directions on one bar: the short wins. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`trailing_stop_pending`
