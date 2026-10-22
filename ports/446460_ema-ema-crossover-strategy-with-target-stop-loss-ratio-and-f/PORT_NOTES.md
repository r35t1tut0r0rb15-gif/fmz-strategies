# #446460 基于目标止损比例和固定仓位的EMA交叉策略-EMA-Crossover-Strategy-with-Target-Stop-loss-Ratio-and-Fixed-Position-Size -> `fmz_446460_ema20_50_cross_reversal`

- FMZ source id: 446460 (lineage).
- Source: https://www.fmz.com/strategy/446460 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 18:04:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Levels plot only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
