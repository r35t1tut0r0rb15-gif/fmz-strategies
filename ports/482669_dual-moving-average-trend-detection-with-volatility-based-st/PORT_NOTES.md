# #482669 双均线趋势判断与波动率止损策略-Dual-Moving-Average-Trend-Detection-with-Volatility-Based-Stop-Loss-Strategy -> `fmz_482669_ema9_21_cross_atr_stop`

- FMZ source id: 482669 (lineage).
- Source: https://www.fmz.com/strategy/482669 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:57:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | Two EMAs and an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `slow` [21, 50]: **4 trials**; defaults 1.5 / 21 (the source's); EMA 9 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

The stop is re-issued every bar from `strategy.position_avg_price` with the current ATR, so it moves with
volatility. The port fixes it at the signal bar's ATR (re-based on the fill). Decision owed as #489289.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
