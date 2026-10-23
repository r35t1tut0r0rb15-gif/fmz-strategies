# #430278 双Stochastics与成交量加权移动平均线组合指标Dual-Stochastics-and-Volume-Weighted-Moving-Average-Combination-Indicator-Strategy -> `fmz_430278_dual_stochastic_sum_vwma_colour_turn_long`

- FMZ source id: 430278 (lineage).
- Source: https://www.fmz.com/strategy/430278 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 17:18:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dual-stochastic trend turns with a volume-weighted signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [30, 14] x `vwma_len` [30, 15]: **4 trials**; second stochastic 90.

## Ambiguities resolved

- Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_trend"`.

## Marks

`none`
