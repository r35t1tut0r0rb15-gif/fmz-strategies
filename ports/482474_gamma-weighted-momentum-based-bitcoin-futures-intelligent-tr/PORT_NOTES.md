# #482474 基于伽马权重和动量的比特币期货智能交易策略-Gamma-Weighted-Momentum-Based-Bitcoin-Futures-Intelligent-Trading-Strategy -> `fmz_482474_gamma_weighted_avg_side_two_bar_momentum`

- FMZ source id: 482474 (lineage).
- Source: https://www.fmz.com/strategy/482474 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:45:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A weighted average and close sequences. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50000 cash per trade. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gamma` [0.75, 0.9] x `length` [60, 30]: **4 trials**; defaults 0.75 / 60 (the source's).

## Ambiguities resolved

- GWAP weights lags 0 to length - 1 of the close by gamma^i; na until bar `length` (as written); the typical price is
  unused. REVERSAL INTENDED (always in). FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
