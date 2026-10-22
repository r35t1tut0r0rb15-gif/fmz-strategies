# #483023 动态趋势跟踪与波动率过滤策略基于ADX与CI双重确认的均线交叉系统-Dynamic-Trend-Following-with-Volatility-Filtering-ADX-and-CI-Dual-Confirmed-Moving-Average-Crossover-System -> `fmz_483023_sma9_21_cross_adx7_20_chop7_50_reversal`

- FMZ source id: 483023 (lineage).
- Source: https://www.fmz.com/strategy/483023 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 09:33:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with ADX / Choppiness filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_thresh` [20.0, 25.0] x `chop_thresh` [50.0, 61.8]: **4 trials**; SMA 9 / 21, ADX 7, CHOP 7.

## Ambiguities resolved

- nz() reads 0 for the first bar's previous values, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
