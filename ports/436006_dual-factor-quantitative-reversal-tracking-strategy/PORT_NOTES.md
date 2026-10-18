# #436006 Dual factor Quantitative Reversal Tracking Strategy -> `fmz_436006_reversal_123_awesome_oscillator`

- FMZ source id: 436006 (lineage).
- Source: https://www.fmz.com/strategy/436006 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 17:26:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and an oscillator slope state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430763. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `slow` [34, 21]: **4 trials**; stochastic 14 / 1 / 3, level 50 and fast 5 fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "20min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
