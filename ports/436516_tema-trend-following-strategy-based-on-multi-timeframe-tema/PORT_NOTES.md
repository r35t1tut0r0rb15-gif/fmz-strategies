# #436516 基于多时间框架TEMA指标交叉的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Timeframe-TEMA-Crossover -> `fmz_436516_tema_cross_htf_filter`

- FMZ source id: 436516 (lineage).
- Source: https://www.fmz.com/strategy/436516 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 14:20:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C91). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Triple-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [60, 40]: **4 trials**; the higher-timeframe lengths 5 / 15 fixed.

## Ambiguities resolved

- Higher-timeframe "D" equals the chart (daily). Orders in call order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
