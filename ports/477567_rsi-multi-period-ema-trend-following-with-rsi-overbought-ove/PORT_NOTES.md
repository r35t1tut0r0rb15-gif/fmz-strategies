# #477567 多周期均线趋势跟踪结合RSI超买超卖动态优化策略-Multi-Period-EMA-Trend-Following-with-RSI-Overbought-Oversold-Dynamic-Optimization-Strategy -> `fmz_477567_ema20_50_trend_rsi_filter_hold5_reversal`

- FMZ source id: 477567 (lineage).
- Source: https://www.fmz.com/strategy/477567 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 14:10:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend states with an RSI filter and a 5-bar hold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold_bars` [5, 10] x `ema_long` [50, 100]: **4 trials**; EMA 20, RSI 14 / 70 / 30, ATR 14.

## Ambiguities resolved

- The hold count runs through a reversal, as written; the ATR threshold is a price amount (fraction of 42000).
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
