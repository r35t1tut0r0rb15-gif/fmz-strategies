# #439052 优化EMA黄金交叉策略Optimized-EMA-Crossover-Strategy -> `fmz_439052_ema7_20_cross_45m`

- FMZ source id: 439052 (lineage).
- Source: https://www.fmz.com/strategy/439052 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 12:01:59). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR-based size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 12] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- Reversal stands on crossing bars. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
