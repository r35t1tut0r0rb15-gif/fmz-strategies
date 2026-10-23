# #475602 多指标趋势跟踪期权交易EMA交叉策略-Multi-Indicator-Trend-Following-Options-Trading-EMA-Cross-Strategy -> `fmz_475602_ema8_21_cross_sma_trend_macd_rsi_flag_target_reversal`

- FMZ source id: 475602 (lineage).
- Source: https://www.fmz.com/strategy/475602 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:49:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked target followed in the signals |
| 2 | PASS | EMA 8 / 21 crossings in the SMA 100 / 200 trend with MACD and RSI |
| 3 | PASS | Exchange pair in the header only (options named in the title). |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.05, 0.1] x `fast` [8, 12]: **4 trials**; EMA 21, SMA 100 / 200, MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- The target runs only after a repeat signal; the short's level is above the entry. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
