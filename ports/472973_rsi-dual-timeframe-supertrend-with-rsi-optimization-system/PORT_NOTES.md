# #472973 双时间周期超级趋势与RSI策略优化系统-Dual-Timeframe-Supertrend-with-RSI-Optimization-System -> `fmz_472973_close_cross_2h_supertrend_15m_rsi_exit_reversal`

- FMZ source id: 472973 (lineage).
- Source: https://www.fmz.com/strategy/472973 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 17:27:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 2-hour and 15-minute values from completed bars; the fill-price target as a fixed fraction |
| 2 | PASS | Higher-time-frame Supertrend crossings with an RSI exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.42, 2.0] x `tp_pct` [0.30, 0.05]: **4 trials**; the ATR 14 and RSI 5 / 95 / 5 fixed.

## Ambiguities resolved

- 2-hour values from the last completed 2-hour bar, 15-minute RSI from the chart bar's last 15 minutes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
