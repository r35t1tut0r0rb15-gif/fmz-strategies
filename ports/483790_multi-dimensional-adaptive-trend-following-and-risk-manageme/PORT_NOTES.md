# #483790 多维度自适应趋势追踪与风险管理策略-Multi-Dimensional-Adaptive-Trend-Following-and-Risk-Management-Strategy -> `fmz_483790_sma_band_cross_trend_window_cooldown`

- FMZ source id: 483790 (lineage).
- Source: https://www.fmz.com/strategy/483790 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-26 09:54:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the break-even stop placed beyond the close acts as a next-open exit. |
| 2 | PASS | Moving averages and ATR; the tick distances as ATR multiples judged on ETH_USDT 1h. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_k` [0.033, 0.066] x `atr_mult` [1.2, 1.5]: **4 trials**; defaults 0.033 / 1.2 (the source's, tp_k converted);
length 10, cooldown 15, ATR 14, the 0.017 ATR stop extra and break-even trigger, the 02:00-14:00 UTC window fixed.

## Tick distances (criterion 2)

On Binance ETH_USDT (mintick 0.01) the 100-tick target is 1.00 USD and the 50-tick distances 0.50 USD; the 1-hour
ATR(14) in the backtest window (Jan-Feb 2025) was about 30 USD, so the target is about 0.033 ATR and the 50-tick
distances about 0.017 ATR. As written the target is a scalp of a few hundredths of an ATR.

## Break-even exit

`strategy.exit("Break Even ...", stop = close +- 2 ticks)` is placed on any bar where the long's high reached close +
50 ticks (short mirrored): a sell stop above the market, which fills at the next open. Ported as an exit signal on
that bar (rule 3), never on an entry-signal bar.

## Ambiguities resolved

- Clock (C6): the window uses the bar's open hour in UTC (the author's Binance chart), 02:00 <= hour < 14:00.
- The cooldown counts bars since the last entry-signal bar (> 15 bars).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
