# #434609 移动平均聚合Williams商业区买卖压力指标策略Moving-Average-Aggregation-Williams-Commercial-Bid-Ask-Pressure-Indicator-Strategy -> `fmz_434609_williams_ad_sma_side`

- FMZ source id: 434609 (lineage).
- Source: https://www.fmz.com/strategy/434609 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-07 17:48:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A price-change accumulation against its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430903. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 30] x `reverse` [False, True]: **4 trials**.

## Ambiguities resolved

- Previous-bar low / high and the reset on unchanged closes, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
