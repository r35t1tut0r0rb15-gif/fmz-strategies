# #489634 多指标结合的自适应波动ATR动态止盈止损15分钟图表趋势跟踪策略-Multi-Indicator-Adaptive-Volatility-ATR-Dynamic-SL-TP-15-Minute-Chart-Trend-Following-Strategy -> `fmz_489634_ema50_side_macd_hist_rsi_band_state_reversal`

- FMZ source id: 489634 (lineage).
- Source: https://www.fmz.com/strategy/489634 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 11:33:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | EMA / MACD / RSI states |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaLength` [50, 100] x `rsiOB` [70, 80]: **4 trials** (oversold 100 minus it); MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
