# #482477 多周期均线趋势跟踪与支阻系统结合的混合交易策略-Multi-Period-EMA-Trend-Following-with-Support-Resistance-Hybrid-Trading-System -> `fmz_482477_breakout_or_ema_trend_state_wide_atr_stop`

- FMZ source id: 482477 (lineage).
- Source: https://www.fmz.com/strategy/482477 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:52:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | Rolling extremes, EMAs and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [9, 20] x `stop_mult` [10, 5]: **4 trials**; defaults 9 / 10 (the source's); ATR 14 and EMA 20 / 50 fixed.

## Trailing stop (mark `trailing_stop_pending`)

The stop is re-issued every bar at the current close -/+ 10 ATR, so it moves with the price (both ways). The port
fixes it at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- Both entry tests read the bar-start position: with both signals the short wins when flat or long, the long when
  short. `simulate()` mirrors the house stop from the fill (as #430254).
- The strategy title's personal contact details are not carried into NAME. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`trailing_stop_pending`
