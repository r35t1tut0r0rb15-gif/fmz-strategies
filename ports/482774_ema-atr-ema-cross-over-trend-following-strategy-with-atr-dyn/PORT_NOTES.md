# #482774 EMA交叉趋势追踪与ATR动态止损优化策略-EMA-Cross-Over-Trend-Following-Strategy-with-ATR-Dynamic-Stop-Loss-Optimization -> `fmz_482774_ema5_200_cross_atr_stop_pct_target_long`

- FMZ source id: 482774 (lineage).
- Source: https://www.fmz.com/strategy/482774 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | Two EMAs, an ATR multiple and a percentage target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `tp_pct` [5, 10]: **4 trials**; defaults 2 / 5 (the source's); EMA 5 / 200 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

The stop is re-issued every bar at the current close - 2 ATR, so it moves with the price (up and down). The port
fixes it at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- The 5 % target is measured from `strategy.position_avg_price`: applied from the fill (decision owed as #489289).
- Long only. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
