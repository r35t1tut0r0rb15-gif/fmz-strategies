# #489737 高效趋势捕捉型指数移动平均线交叉与动态追踪止损策略-Advanced-Trend-Capture-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop -> `fmz_489737_ema13_33_side_tick_trail`

- FMZ source id: 489737 (lineage).
- Source: https://www.fmz.com/strategy/489737 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-08 10:23:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail a house trail (approximation stated). |
| 2 | ADAPT | 2-tick trail -> a fraction of price; the price-unit activation is immediate. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 20 % of equity quoted (slippage 5 is a cost); the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND489653 (2 members, best partner #489653, Jaccard 0.651). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.000007, 0.01] x `long_ema` [33, 50]: **4 trials**; defaults 0.000007 / 33 (the source's
equivalents); EMA 13 fixed.

## Trailing stop (mark `trailing_stop`)

As written, every bar while in a trade: `strategy.exit(trail_offset = 2, trail_price = high - 10)` (shorts: low +
10): the activation level is below the price at once, then the stop trails 2 ticks behind the best price. Ported as
the house trail `{"type": "percent", "pct": 0.000007, "anchor": "high_low"}` with no activation. **Stated
approximation:** 2 ticks of 0.01 on ETH_USDT at about 3000. As written the trade closes on the first small retrace
and the next bar re-enters. Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- The trail block sets isExiting before the EMA exits, so those exits never run (dead code, not emitted).
- On EMA 13 == EMA 33 the short (written last) wins. REVERSAL INTENDED. Broker-day bars; FREQ = "1D";
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop, trailing_stop`
