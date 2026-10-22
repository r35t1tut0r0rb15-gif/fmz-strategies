# #442077 基于EMA指标的趋势跟踪交易策略EMA-Crossover-Trend-Following-Trading-Strategy -> `fmz_442077_ema3_30_cross_double_target_long`

- FMZ source id: 442077 (lineage).
- Source: https://www.fmz.com/strategy/442077 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 10:39:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and close-vs-fill target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442077. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 9] x `profit_pct` [100.0, 50.0]: **4 trials**; slow EMA 30 fixed.

## Ambiguities resolved

- Close-vs-fill target. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
