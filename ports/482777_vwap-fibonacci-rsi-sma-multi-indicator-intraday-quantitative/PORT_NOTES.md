# #482777 多指标整合日内量化交易策略基于VWAP-Fibonacci-RSI-SMA的动态信号系统-Multi-Indicator-Intraday-Quantitative-Trading-Strategy-Dynamic-Signal-System-Based-on-VWAP-Fibonacci-RSI-SMA -> `fmz_482777_close_sma9_cross_rsi70_range_sell_reversal`

- FMZ source id: 482777 (lineage).
- Source: https://www.fmz.com/strategy/482777 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:50:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 9 crossings with an RSI-70 sell branch |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [9, 20] x `rsi_hi` [70.0, 65.0]: **4 trials**; RSI 14.

## Ambiguities resolved

- Daily VWAP = the close: the RSI buy branch is dead. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
