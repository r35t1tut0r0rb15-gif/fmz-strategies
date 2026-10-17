# #483044 动态多指标优化趋势追踪策略-Dynamic-Multi-Indicator-Optimized-Trend-Following-Strategy -> `fmz_483044_cloud_macd_weekly_trend_bbwidth_2d`

- FMZ source id: 483044 (lineage).
- Source: https://www.fmz.com/strategy/483044 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:46:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed weekly values; the stop from the signal bar (marked). |
| 2 | PASS | Ichimoku spans, MACD, Bollinger width, a weekly SMA and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `bbw_min` [0.02, 0.05]: **4 trials**; defaults 1.5 / 0.02 (the source's); Ichimoku 9 / 26 /
52, MACD 12 / 26 / 9, ATR 14 and the 50-week SMA fixed.

## Trailing stop (mark `trailing_stop_pending`)

Every bar in the condition re-issues the exit with a new 1.5 ATR stop from that bar's close. The port keeps the
entry's stop. No target.

## Ambiguities resolved

- `request.security("W", close > sma(close, 50))`: the last completed week (house rule), weeks of broker days from the
  port's own bars; a two-day block belongs to the week of its first session.
- `hist > -0.05` is a price-unit level, about 0 on ETH's two-day histogram: read as `hist > 0`.
- With BB width above the threshold at every signal, the stop is always the ATR branch.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day blocks of broker-day dates from 1970-01-01
  (decision owed, as #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
