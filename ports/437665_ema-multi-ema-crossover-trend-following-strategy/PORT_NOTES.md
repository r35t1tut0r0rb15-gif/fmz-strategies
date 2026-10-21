# #437665 多重EMA均线交叉趋势跟踪策略Multi-EMA-Crossover-Trend-Following-Strategy -> `fmz_437665_ema12_multi_cross`

- FMZ source id: 437665 (lineage).
- Source: https://www.fmz.com/strategy/437665 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-04 16:22:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 4 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`shortest` [12, 8] x `shorter` [26, 20]: **4 trials**; EMA 50 / 100 / 200 fixed.

## Ambiguities resolved

- Level-less exits place no order; pyramiding adds left out; a bar with both setups ends short. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
