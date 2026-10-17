# #484096 动态色彩阈值波动分析交易策略-Dynamic-Color-Threshold-Volatility-Analysis-Trading-Strategy -> `fmz_484096_smoothed_candle_colour_flip`

- FMZ source id: 484096 (lineage).
- Source: https://www.fmz.com/strategy/484096 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:59:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (re-placement marked). |
| 2 | ADAPT | 20 / 40 ticks -> 0.001 / 0.002 ATR; smoothed candles. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.001, 1.0] x `trade_type` ["Both", "Long Only"]: **4 trials**; defaults 0.001 / Both (the source as
written: on 2-day ETH_USDT, tick 0.01 and ATR about 200, 20 ticks are about 0.001 ATR; judgement stated before any
backtest); target 2 x the stop and the 1 % colour threshold fixed.

## Ambiguities resolved

- A colour change below the threshold emits nothing, so the next one can repeat the side while held and re-place
  the bracket (mark `trailing_stop_pending`; the port keeps the entry's). Closes act on the position at the bar's
  start (#430850). REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day bars are blocks
  of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
