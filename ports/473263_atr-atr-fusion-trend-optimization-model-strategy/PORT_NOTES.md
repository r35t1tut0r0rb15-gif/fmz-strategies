# #473263 ATR融合趋势优化模型策略-ATR-Fusion-Trend-Optimization-Model-Strategy -> `fmz_473263_fib_weighted_buying_pressure_ratio_cross_reversal`

- FMZ source id: 473263 (lineage).
- Source: https://www.fmz.com/strategy/473263 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:06:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Buying-pressure ratio crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_th` [58, 55] x `short_th` [42, 45]: **4 trials**; the ratio lengths fixed.

## Ambiguities resolved

- Partial take-profits off (default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
