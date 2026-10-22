# #446758 移动平均线SMA交叉的多头空头策略-SMA-Crossover-Compounding-Strategy -> `fmz_446758_sma9_21_cross_compounding_reversal`

- FMZ source id: 446758 (lineage).
- Source: https://www.fmz.com/strategy/446758 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-01 11:11:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The compounding quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Compounding quantity is sizing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
