# #486562 多时间框架趋势追踪与ATR波动率动态风险管理系统策略-Multi-Timeframe-Trend-Following-with-ATR-Volatility-Based-Dynamic-Risk-Management-System-Strategy -> `fmz_486562_ema9_21_cross_rsi_macd_15m_sma50_filter_reversal`

- FMZ source id: 486562 (lineage).
- Source: https://www.fmz.com/strategy/486562 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:20:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close bracket pending |
| 2 | PASS | EMA crossings with RSI / MACD / 15-minute trend filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [9, 5] x `slow_length` [21, 50]: **4 trials**; RSI 14, MACD 12 / 26 / 9, 15-minute SMA 50.

## Ambiguities resolved

- The lower-time-frame security is the hour's last 15-minute bar. The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
