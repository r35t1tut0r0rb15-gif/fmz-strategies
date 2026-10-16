# #427396 Stochastics Crossover Trading Strategy -> `fmz_427396_slow_stochastic_state`

- FMZ source id: 427396 (lineage).
- Source: https://www.fmz.com/strategy/427396 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 17:05:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator state. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [35, 14] x `period_d` [21, 9] x `smooth_k` [21, 9]: **8 trials**; defaults 35 / 21 / 21 (the source's).

## Ambiguities resolved

- The test window is the constant true. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
