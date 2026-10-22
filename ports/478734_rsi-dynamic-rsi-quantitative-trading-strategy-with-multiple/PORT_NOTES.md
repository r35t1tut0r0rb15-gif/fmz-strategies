# #478734 多均线交叉辅助RSI动态参数量化交易策略-Dynamic-RSI-Quantitative-Trading-Strategy-with-Multiple-Moving-Average-Crossover -> `fmz_478734_rsi14_ema50_wma100_cross_long`

- FMZ source id: 478734 (lineage).
- Source: https://www.fmz.com/strategy/478734 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:14:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma2_length` [50, 20] x `ma3_length` [100, 50]: **4 trials**; RSI 14.

## Ambiguities resolved

- Default MA types. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
