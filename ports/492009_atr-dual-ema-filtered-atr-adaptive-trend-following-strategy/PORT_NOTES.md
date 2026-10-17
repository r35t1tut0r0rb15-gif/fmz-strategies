# #492009 双均线过滤的ATR自适应趋势跟踪策略-Dual-EMA-Filtered-ATR-Adaptive-Trend-Following-Strategy -> `fmz_492009_utbot_heikin_ashi_ema_filter`

- FMZ source id: 492009 (lineage).
- Source: https://www.fmz.com/strategy/492009 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-25 15:01:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick trail is a house trail (approximation stated). |
| 2 | ADAPT | Tick trail -> ATR multiple; the price-unit target (inert on DOGE) dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the exit quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 2.0] x `trail_k` [0.05, 0.5]: **4 trials**; defaults 1.0 / 0.05 (the source's 1.0 and the tick
trail's ATR equivalent); ATR 20, EMA 10 / 50, Heikin-Ashi on and the activation 0.05 % fixed.

## Trailing stop (mark `trailing_stop`)

As written: `strategy.exit(trail_points = 10, trail_offset = 10, limit = sr +- 100)` every bar. Ported as the house
trail `{"type": "volatility", "atr_n": 20, "k": 0.05, "anchor": "high_low", "activate_after": 0.0005}`. **Stated
approximation:** 10 ticks of 0.00001 on DOGE_USDT at about 0.2 are 0.05 % of price, about 0.05 x the hourly ATR(20).
The `limit` is in price units (+- 100 on a price near 0.2): never reachable on the author's market, so dropped as
inert. Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- The Heikin-Ashi close of the chart's own timeframe is the current bar's (o + h + l + c) / 4.
- The UT Bot line as written (nz(trail[1]) = 0 at the start). Every signal bar is an entry; strategy.close on the
  opposite signal coincides with the reversing entry.
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`trailing_stop`
