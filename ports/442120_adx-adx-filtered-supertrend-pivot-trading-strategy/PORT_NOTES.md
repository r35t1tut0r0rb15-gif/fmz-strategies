# #442120 基于超趋势支撑阻力与ADX指标的高频交易策ADX-Filtered-SuperTrend-Pivot-Trading-Strategy -> `fmz_442120_pivot_supertrend_adx_sma21_long`

- FMZ source id: 442120 (lineage).
- Source: https://www.fmz.com/strategy/442120 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 15:01:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot SuperTrend, ADX and SMA filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the sell order uses the default quantity). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pp_prd` [2, 3] x `atr_factor` [5.0, 3.0]: **4 trials**; ATR 20, ADX 14 / 25 and SMA 21 fixed.

## Ambiguities resolved

- Strict pivots confirmed 2 bars later; the sell order closes the long. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
