# #435897 Heikin-Ashi与考夫曼自适应移动平均线交易策略Heikin-Ashi-and-Kaufman-Adaptive-Moving-Average-Trading-Strategy -> `fmz_435897_hlc3_kaufman_cross`

- FMZ source id: 435897 (lineage).
- Source: https://www.fmz.com/strategy/435897 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-19 15:51:30). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `sloma` [20, 30]: **4 trials**; fast 2.5 and slow 20 fixed.

## Ambiguities resolved

- Previous bar's HLC3; Kaufman from zero. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
