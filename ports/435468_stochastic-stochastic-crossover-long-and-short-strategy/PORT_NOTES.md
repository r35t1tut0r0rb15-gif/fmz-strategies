# #435468 基于Stochastic指标的长短交叉策略Stochastic-Crossover-Long-and-Short-Strategy -> `fmz_435468_stochastic_cross_state`

- FMZ source id: 435468 (lineage).
- Source: https://www.fmz.com/strategy/435468 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-15 10:29:29). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic cross state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length` [7, 14]: **4 trials**; %D 3, levels 70 / 20 fixed.

## Ambiguities resolved

- Fade reading as written; reverse input in the grid. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
