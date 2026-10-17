# #490804 多指标协同短线趋势跟踪策略-Multi-Indicator-Synergistic-Short-Term-Trend-Following-Strategy -> `fmz_490804_macd_ema_rsi_target_atr_trail`

- FMZ source id: 490804 (lineage).
- Source: https://www.fmz.com/strategy/490804 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-16 15:56:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at the signal bar; the trail a house trail (approximations stated). |
| 2 | PASS | EMA, MACD, RSI, a percentage and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [1.0, 3.0] x `atr_mult` [0.8, 1.6]: **4 trials**; defaults 1 / 0.8 (the source's); EMA 20, MACD 6 / 13 / 6,
RSI 9 and the 2.4 % activation fixed.

## Trailing stop (mark `trailing_stop`)

As written, on the entry bar: `strategy.exit(limit = close x (1 +- 1 %), trail_points = trail_offset = ATR x 0.8)`.
The trail arguments take ticks; the author passes ATR price distances, read as price distances (as #427592). Ported
as `tp_stop` 0.01 plus the house trail `{"type": "volatility", "atr_n": 14, "k": 0.8, "anchor": "high_low",
"activate_after": 0.024}`. **Stated approximations:** Pine fixes the distances at the entry bar's ATR; the 0.8-ATR
activation becomes a 2.4 % gain (0.8 daily ATR on BTC_USDT), so on that market the 1 % target usually comes first,
as in the source. Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- Every signal bar is an entry; entries reverse. REVERSAL INTENDED. Broker-day bars; FREQ = "1D";
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop, trailing_stop`
