# #482501 指数移动平均线交叉脉冲趋势分析交易策略-Exponential-Moving-Average-Cross-Impulsive-Trend-Analysis-Trading-Strategy -> `fmz_482501_ema10_cross_impulse_pullback_impulse`

- FMZ source id: 482501 (lineage).
- Source: https://www.fmz.com/strategy/482501 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 17:41:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a stop set at entry. |
| 2 | PASS | An EMA, candle direction and the signal bar's range; the tick body and the level target dropped as inert. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [10, 20]: **2 trials**; default 10 (the source's). The pattern has no other signal parameter that acts.

## Ambiguities resolved

- The 10-tick body minimum is a fraction of a dollar on BTC_USDT: dropped as inert (as #492009).
- `profit=` takes ticks but receives a price level (close + 3 R); read as a price distance (#427592) it is
  unreachable: dropped. Trades end at the stop (the signal bar's low / high) or on a reversal.
- The bar counters start at 0, so the pattern can fire before the first cross (as written). A shared long / short
  bar keeps the short (written later).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
