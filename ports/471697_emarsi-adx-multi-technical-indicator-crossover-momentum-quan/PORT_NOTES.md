# #471697 多重技术指标交叉动量量化交易策略-基于EMARSI和ADX的整合分析-Multi-Technical-Indicator-Crossover-Momentum-Quantitative-Trading-Strategy-Integration-Analysis-Based-on-EMA-RSI-and-ADX -> `fmz_471697_ema9_21_cross_rsi_adx_filter_long`

- FMZ source id: 471697 (lineage).
- Source: https://www.fmz.com/strategy/471697 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:14:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the bracket armed only by a repeat signal not ported (mark) |
| 2 | PASS | EMA crossings with RSI and ADX filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND471697. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `adx_th` [20, 25]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Repeat-signal bracket not ported (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
