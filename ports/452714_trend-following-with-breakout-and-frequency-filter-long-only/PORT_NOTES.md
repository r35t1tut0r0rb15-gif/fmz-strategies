# #452714 Trend-Following-with-Breakout-and-Frequency-Filter-Long-Only-基于突破和频率过滤的趋势跟踪策略只做多 -> `fmz_452714_lagged_120bar_high_breakout_ema50_long`

- FMZ source id: 452714 (lineage).
- Source: https://www.fmz.com/strategy/452714 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 14:00:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark) |
| 2 | PASS | Old-high breakouts in an EMA uptrend |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `lb_min` [80, 40] x `sl_pct` [0.02, 0.05]: **8 trials**; the 120-bar window fixed.

## Ambiguities resolved

- The millisecond hold is no filter; re-issued stops pending. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
