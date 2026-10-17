# #491514 RSI与SuperTrend过滤策略组合系统趋势确认下的动量反转交易框架-RSI-and-SuperTrend-Filter-Combination-System-Momentum-Reversal-Trading-Framework-with-Trend-Confirmation -> `fmz_491514_rsi_turn_supertrend_dir_bracket`

- FMZ source id: 491514 (lineage).
- Source: https://www.fmz.com/strategy/491514 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-21 16:31:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | Oscillator levels, ATR bands and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_oversold` [35, 30] x `atr_mult` [3.0, 2.0]: **4 trials**; defaults 35 / 3.0 (the source's); RSI 14, overbought
65, ATR 10, TP 1.5 %, SL 1 % fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

As written, `strategy.exit(limit = close x (1 +- 1.5 %), stop = close x (1 -+ 1 %))` is re-issued at every bar's
close, so both levels follow the price. The port fixes them at entry: `sl_stop` 0.01, `tp_stop` 0.015 of the fill
price. Daily bars: `coarse_bar_stop`.

## Ambiguities resolved

- The direction is the source's own two-band test (no ratchet), as written.
- The title's "45m BTCUSDT" is a label only; the backtest header is 1d.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
