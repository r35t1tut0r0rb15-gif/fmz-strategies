# #474959 多周期均线穿越结合RSI动量与ATR波动率的趋势跟踪策略-Multi-Period-EMA-Crossover-with-RSI-Momentum-and-ATR-Volatility-Based-Trend-Following-Strategy -> `fmz_474959_engulfing_ema100_200_rsi50_atr_bracket_long`

- FMZ source id: 474959 (lineage).
- Source: https://www.fmz.com/strategy/474959 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:33:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR bracket from the fill |
| 2 | PASS | Trend engulfing candles with an RSI filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [100, 50] x `long_ema` [200, 100]: **4 trials**; RSI 50, ATR 1.1 / 2.

## Ambiguities resolved

- ATR of the bar before the fill; the per-bar ATR moves pending. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
