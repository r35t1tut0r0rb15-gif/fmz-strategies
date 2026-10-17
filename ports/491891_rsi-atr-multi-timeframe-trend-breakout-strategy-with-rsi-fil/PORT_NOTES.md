# #491891 多时间框架趋势突破策略与RSI过滤及ATR风险管理-Multi-Timeframe-Trend-Breakout-Strategy-with-RSI-Filter-and-ATR-Based-Risk-Management -> `fmz_491891_ema_trend_breakout_rsi_atr_bracket`

- FMZ source id: 491891 (lineage).
- Source: https://www.fmz.com/strategy/491891 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 16:55:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar; the trail pending (mark). |
| 2 | PASS | EMAs, RSI and ATR multiples. |
| 3 | PASS | No exchange-only feature. |
| 4 | DONE | 2 %-risk quantity quoted; the bracket via `stops()`; all exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.0] x `tp_ratio` [3.0, 1.5]: **4 trials**; defaults 2.0 / 3.0 (the source's); EMA 9 / 21, RSI 14,
ATR 14 fixed. No bar size: the driver's bar-size search supplies it.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, on the entry bar: `strategy.exit(stop, limit, trail_points = ATR x 2 x 3 x 0.5, trail_offset = ATR x 2)`.
The two trail arguments take ticks; the author passes ATR price distances, read as price distances (as #427592):
once the trade is 3 ATR (signal bar's) in profit, a stop trails 2 ATR behind the best price, on top of the fixed
stop and target. The house trail's `activate_after` is a fixed fraction of price; an ATR-measured activation cannot
be expressed, and with no bar size no fraction can be judged, so the trail is not emitted. Decision owed: whether to
emit it as `{"type": "volatility", "atr_n": 14, "k": 2, "anchor": "high_low", "activate_after": <fraction>}` once the
bar size is chosen.

## Ambiguities resolved

- No backtest header: `FREQ = "bar_size_pending"`, bars from `bar_sizes.build_bars(raw_1m_df, params["bar_size"])`.
- Every signal bar is an entry; entries reverse (REVERSAL INTENDED).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`bar_size_pending, trailing_stop_pending`
