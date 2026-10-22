# #481094 Logarithmic-Weighted-Moving-Average-Trading-Strategy-Based-on-Cross-Signal-Analysis-基于对数加权移动平均交叉信号的量化交易策略 -> `fmz_481094_log_wma5_20_cross_reversal`

- FMZ source id: 481094 (lineage).
- Source: https://www.fmz.com/strategy/481094 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-08 14:53:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Log-price WMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [5, 10] x `long_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
