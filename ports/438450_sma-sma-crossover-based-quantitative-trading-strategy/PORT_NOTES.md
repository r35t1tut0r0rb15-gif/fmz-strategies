# #438450 基于SMA均线交叉的量化交易策略SMA-Crossover-Based-Quantitative-Trading-Strategy -> `fmz_438450_sma5_200_cross_long_held`

- FMZ source id: 438450 (lineage).
- Source: https://www.fmz.com/strategy/438450 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 10:51:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [200, 130]: **4 trials**.

## Ambiguities resolved

- close() names an unused id: the first long is held. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
