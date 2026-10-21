# #436788 多周期EMA交叉量化交易策略Multi-Period-EMA-Crossover-Quantitative-Trading-Strategy -> `fmz_436788_ema_stack_long_only`

- FMZ source id: 436788 (lineage).
- Source: https://www.fmz.com/strategy/436788 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 17:09:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA alignment |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p1` [10, 20] x `p2` [100, 50]: **4 trials**; EMA 200 fixed.

## Ambiguities resolved

- Date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
