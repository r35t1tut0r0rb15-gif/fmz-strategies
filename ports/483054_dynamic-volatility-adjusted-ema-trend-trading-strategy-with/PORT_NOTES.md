# #483054 动态波动率跟踪均线趋势交易策略与智能止损系统-Dynamic-Volatility-Adjusted-EMA-Trend-Trading-Strategy-with-Smart-Stop-Loss-System -> `fmz_483054_ema9_21_atr_extension_close_stop`

- FMZ source id: 483054 (lineage).
- Source: https://www.fmz.com/strategy/483054 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:11:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-based stop is an exit signal. |
| 2 | PASS | Moving averages, RSI, ATR multiples and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 1.0] x `stop_pct` [1.0, 2.0]: **4 trials**; defaults 1.5 / 1 (the source's); EMA 9 / 21, RSI 14
(70 / 30) and ATR 14 fixed.

## Ambiguities resolved

- The lengths depend on the chart timeframe; on the header's 1-minute chart they are 9 / 21 / 14.
- The 1 % stop is checked on closes and acts through `strategy.close`: an exit signal at the next open (rule 3, as
  #489638). No stop module.
- close + entry is a reversal. Target-position state machine, exits only on going flat. REVERSAL INTENDED.
  FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
