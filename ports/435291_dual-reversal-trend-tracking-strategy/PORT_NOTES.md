# #435291 Dual Reversal Trend Tracking Strategy -> `fmz_435291_reversal_123_performance_index`

- FMZ source id: 435291 (lineage).
- Source: https://www.fmz.com/strategy/435291 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 18:01:53). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a percent change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `period` [14, 28]: **4 trials**; stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
