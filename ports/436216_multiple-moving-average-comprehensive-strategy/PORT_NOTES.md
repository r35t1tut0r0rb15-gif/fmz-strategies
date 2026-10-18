# #436216 Multiple Moving Average Comprehensive Strategy -> `fmz_436216_close_vs_ten_smas`

- FMZ source id: 436216 (lineage).
- Source: https://www.fmz.com/strategy/436216 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 11:56:42). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average stack |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`step` [10, 20] x `n_ma` [10, 5]: **4 trials**; the averages are step, 2 step, ... n_ma step.

## Ambiguities resolved

- Close beyond all averages; states every bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
