# #436009 基于EMA均线交叉的移动止损策略EMA-Crossover-Strategy-with-Trailing-Stop-Loss -> `fmz_436009_ema_9_21_cross_no_exit`

- FMZ source id: 436009 (lineage).
- Source: https://www.fmz.com/strategy/436009 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 17:39:30). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | The trailing stop never exists: no exit as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 34]: **4 trials**.

## Ambiguities resolved

- The trailing stop never exists: no exit. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
