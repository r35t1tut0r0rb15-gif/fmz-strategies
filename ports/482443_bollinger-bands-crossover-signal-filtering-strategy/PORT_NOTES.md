# #482443 布林带交叉信号筛选交易策略-Bollinger-Bands-Crossover-Signal-Filtering-Strategy -> `fmz_482443_bb55_last_side_switch_always_in`

- FMZ source id: 482443 (lineage).
- Source: https://www.fmz.com/strategy/482443 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:47:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 30] x `mult` [1.0, 2.0]: **4 trials**; defaults 55 / 1 (the source's).

## Ambiguities resolved

- `barssince` is na before its first event; comparisons with na are false.
- REVERSAL INTENDED (always in). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
