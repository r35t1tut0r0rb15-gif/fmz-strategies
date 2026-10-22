# #489039 双模式自适应趋势交易策略EMA交叉结合ATR波动率风险管理系统-Dual-Mode-Adaptive-Trend-Trading-Strategy-EMA-Crossover-with-ATR-Volatility-Based-Risk-Management-System -> `fmz_489039_ema3_8_cross_adaptive_trend_counter_atr_bracket_flat`

- FMZ source id: 489039 (lineage).
- Source: https://www.fmz.com/strategy/489039 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 14:20:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings, trend or counter-trend by RSI distance, with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized leveraged quantity and margins stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tradeInterval` [72, 10] x `slMultiplier` [1.2, 2.0]: **4 trials**; EMA 3 / 8 / 55, ATR 14, TP 2 ATR, RSI 14.

## Ambiguities resolved

- The interval is in bars, from bar 0 of the data. Entries only from flat (a loop follows the bracket). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
