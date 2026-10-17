# #433544 动量策略的RSI指标聚合RSI-Momentum-Aggregation-Strategy -> `fmz_433544_rsi_30_70_cross_1h`

- FMZ source id: 433544 (lineage).
- Source: https://www.fmz.com/strategy/433544 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 15:01:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [30, 20]: **4 trials**; the short level is 100 - oversold (70 as written).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
