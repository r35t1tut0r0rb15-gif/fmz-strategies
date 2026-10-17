# #484914 增强型动态通道突破趋势跟踪交易系统-Enhanced-Dynamic-Channel-Breakout-Trend-Following-Trading-System -> `fmz_484914_donchian_turtle_sma_rsi_stop`

- FMZ source id: 484914 (lineage).
- Source: https://www.fmz.com/strategy/484914 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 09:49:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and bar-range-checked exits; stop fixed at entry (marked). |
| 2 | PASS | Channels, a moving average, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-unit quantity and add-ons quoted; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_period` [15, 20] x `stop_mult` [2.0, 3.0]: **4 trials**; defaults 15 / 2 (the source's); exit channel 5, ATR
10, SMA 200 and RSI 14 (30 / 70) fixed.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, every bar in a long: `longTrailingStop := max(longTrailingStop[1], avg price - 2 x ATR)` with the
CURRENT ATR, and the variable is never reset, so a later long starts from the previous long's level (shorts
mirrored). Not expressible in the house trail; fixed at entry here (2 ATR of the signal bar, re-based on the fill).

## Ambiguities resolved

- The channel exits are bar-range-checked: exit signals at the next open (#489638), from the position at the bar's
  start (#430850). `close_all` + entry is the reversal: REVERSAL INTENDED. The add-unit entries cannot fill (default
  pyramiding 1). `simulate()` mirrors the stop from the fill bar (#430254). Stop module: `portfolio_kwargs` {} (D4).
  Daily bars are broker days; FREQ = "1D" ("BTC 1H" is a label): `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
