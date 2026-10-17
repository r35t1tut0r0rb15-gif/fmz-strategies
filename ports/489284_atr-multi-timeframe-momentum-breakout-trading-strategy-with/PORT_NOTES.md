# #489284 多时间框架动量突破交易策略结合趋势跟踪与ATR风险管理-Multi-Timeframe-Momentum-Breakout-Trading-Strategy-with-Trend-Following-and-ATR-Risk-Management -> `fmz_489284_breakout_ema_trend_atr_stop_trail`

- FMZ source id: 489284 (lineage).
- Source: https://www.fmz.com/strategy/489284 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 15:17:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (mark); the trail a house trail. |
| 2 | PASS | EMAs, RSI, channel breakouts and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`breakout` [5, 20] x `atr_mult` [1.5, 3.0]: **4 trials**; defaults 5 / 1.5 (the source's); EMA 20 / 50, RSI 14
(70 / 30) and the 6 % activation fixed.

## Stops (marks `trailing_stop_pending`, `trailing_stop`)

As written, every bar in a position: `strategy.exit(stop = avg price -+ 1.5 x ATR, trail_points = trail_offset =
1.5 x ATR)`. The stop moves with the current ATR: fixed at the signal bar here (`trailing_stop_pending`). The trail
arguments (ticks, given ATR price distances, read as price distances as #427592) become the house trail
`{"type": "volatility", "atr_n": 14, "k": 1.5, "anchor": "high_low", "activate_after": 0.06}`; **stated
approximation:** the 1.5-ATR activation becomes a 6 % gain (1.5 daily ATR on BNB_USDT). Promotion of a trailing
trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- Every condition bar is an entry; entries reverse. REVERSAL INTENDED. Broker-day bars; FREQ = "1D";
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop, trailing_stop_pending`
