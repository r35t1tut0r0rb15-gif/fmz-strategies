# #450860 MOST与双均线交叉策略-MOST-and-Dual-Moving-Average-Crossover-Strategy -> `fmz_450860_sma14_21_cross_reversal`

- FMZ source id: 450860 (lineage).
- Source: https://www.fmz.com/strategy/450860 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-09 16:23:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 9] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
