# #436246 Empirical Mode Decomposition Based Quantitative Trading Strategy -> `fmz_436246_empirical_mode_state`

- FMZ source id: 436246 (lineage).
- Source: https://www.fmz.com/strategy/436246 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 14:41:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-pass filter state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430069. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length` [20, 30]: **4 trials**; delta 0.5 and fraction 0.1 fixed.

## Ambiguities resolved

- Author's pi 3.1415; filter from zero. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`
