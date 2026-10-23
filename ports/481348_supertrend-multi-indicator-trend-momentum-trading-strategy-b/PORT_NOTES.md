# #481348 基于SuperTrend的多指标趋势动量交易策略Multi-Indicator-Trend-Momentum-Trading-Strategy-Based-on-SuperTrend -> `fmz_481348_supertrend_flip_2d_long_only`

- FMZ source id: 481348 (lineage).
- Source: https://www.fmz.com/strategy/481348 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-10 14:31:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 14] x `mult` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- VWAP / EMA / DMI plot only. Long only. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
