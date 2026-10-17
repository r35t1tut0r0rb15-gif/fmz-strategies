# #489651 动态趋势过滤ATM期权卖出策略结合EMA交叉与RSI动量确认-Dynamic-Trend-Filtered-ATM-Option-Selling-Strategy-with-EMA-Crossover-and-RSI-Momentum-Confirmation -> `fmz_489651_ema_cross_both_sides_short_bracket`

- FMZ source id: 489651 (lineage).
- Source: https://www.fmz.com/strategy/489651 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 13:29:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 50-point distances -> `bracket_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed 375 quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bracket_atr` [5.0, 2.0] x `rsi_len` [14, 7]: **4 trials**; defaults 5 / 14; EMA 9 / 15 and SMA 50 / 80 fixed. On
daily DOGE_USDT (tick 0.00001 at about 0.17) 50 points (100 ticks each) are 0.05, about 30 % and about 5 daily ATR
(judgement, stated before any backtest).

## Ambiguities resolved

- Both "sell call" and "sell put" call `strategy.short`: short only, as written (the option legs are not modelled).
- The 15:24 close-all never matches a daily bar: not emitted (check 9 noted in the docstring).
- Opposite entries cannot occur. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
