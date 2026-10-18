# #436094 Dual Indicator Quantitative Strategy -> `fmz_436094_reversal_123_ravi`

- FMZ source id: 436094 (lineage).
- Source: https://www.fmz.com/strategy/436094 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 10:59:16). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a percent index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `fast_ma` [7, 5]: **4 trials**; slow 65, trade line 0.14, stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
