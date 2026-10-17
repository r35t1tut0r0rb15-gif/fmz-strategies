# #489333 高级价格行情突破与反转检测策略-Advanced-Price-Action-Breakout-and-Reversal-Detection-Strategy -> `fmz_489333_pin_bar_or_close_breakout_bracket`

- FMZ source id: 489333 (lineage).
- Source: https://www.fmz.com/strategy/489333 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 15:09:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 10 / 30 pips -> `sl_atr` x ATR(14) and 3 x that. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.15, 0.5] x `rr` [3.0, 1.5]: **4 trials**; defaults 0.15 / 3; breakout 5 closes fixed. The title names
EUR/USD, where 10 pips are about 0.15 daily ATR (on the backtest's BTC_USDT they would be a negligible 0.004 ATR);
judgement, stated before any backtest.

## Ambiguities resolved

- `trail_points` without `trail_offset` starts no trailing stop in Pine: inert.
- The 13-14 h exclusion never touches a daily bar (stamped at the broker-day start): always true, not emitted.
- Both signals on one bar: the short wins. REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action_breakout"`.

## Marks

`coarse_bar_stop`
