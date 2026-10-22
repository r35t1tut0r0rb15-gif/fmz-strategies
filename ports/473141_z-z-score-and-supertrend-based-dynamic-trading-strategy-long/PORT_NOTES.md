# #473141 基于Z分数和超级趋势的动态交易策略多空切换系统-Z-Score-and-Supertrend-Based-Dynamic-Trading-Strategy-Long-Short-Switching-System -> `fmz_473141_zscore75_rsi_supertrend_confirm_reversal`

- FMZ source id: 473141 (lineage).
- Source: https://www.fmz.com/strategy/473141 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:01:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Z-score extremes with RSI and Supertrend confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [75, 50] x `factor` [2.0, 3.0]: **4 trials**; the z thresholds and RSI levels fixed.

## Ambiguities resolved

- direction < 0 is Pine's up trend (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
