# #453234 TEMA双均线交叉策略-TEMA-Dual-Moving-Average-Crossover-Strategy -> `fmz_453234_tema9_26_cross_reversal`

- FMZ source id: 453234 (lineage).
- Source: https://www.fmz.com/strategy/453234 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 10:59:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TEMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital setting stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [9, 5] x `len2` [26, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
