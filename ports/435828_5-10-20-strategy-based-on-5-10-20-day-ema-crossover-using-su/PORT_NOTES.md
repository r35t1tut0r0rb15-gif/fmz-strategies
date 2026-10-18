# #435828 基于超趋势的5日10日20日均线交叉策略Strategy-Based-on-5-10-20-Day-EMA-Crossover-Using-Super-Trend-Confirmation -> `fmz_435828_ema_stack_supertrend`

- FMZ source id: 435828 (lineage).
- Source: https://www.fmz.com/strategy/435828 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 10:39:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average stack and a trend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [5, 3] x `mult` [2.0, 3.0]: **4 trials**; EMA 10 / 20 and ATR 14 fixed.

## Ambiguities resolved

- State conditions; built-in Supertrend. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
