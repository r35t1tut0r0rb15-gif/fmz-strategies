# #437552 DEMA与TEMA交叉策略Dual-and-Triple-Exponential-Moving-Average-Crossover-Strategy -> `fmz_437552_dema_tema_cross`

- FMZ source id: 437552 (lineage).
- Source: https://www.fmz.com/strategy/437552 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 16:47:08). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dema_length` [10, 20] x `tema_length` [8, 16]: **4 trials**.

## Ambiguities resolved

- Signals only, reversing. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
