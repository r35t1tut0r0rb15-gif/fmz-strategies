# #436148 Moment Reversal Strategy Based on Multi factor Model -> `fmz_436148_reversal_123_confluence`

- FMZ source id: 436148 (lineage).
- Source: https://www.fmz.com/strategy/436148 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 16:26:10). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a smoothed-average score |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433002. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `harmonic` [10, 8]: **4 trials**; bands +-9, stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- Round half up; angles as written; neutral state closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
