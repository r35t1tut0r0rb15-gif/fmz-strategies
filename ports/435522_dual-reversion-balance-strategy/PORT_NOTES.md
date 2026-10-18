# #435522 Dual Reversion Balance Strategy -> `fmz_435522_reversal_123_empirical_mode`

- FMZ source id: 435522 (lineage).
- Source: https://www.fmz.com/strategy/435522 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 16:56:20). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a band-pass filter state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435522. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length_emd` [20, 30]: **4 trials**; stochastic 14 / 1 / 3, level 50, delta 0.5 and fraction 0.1 fixed.

## Ambiguities resolved

- Author's pi 3.1415; filter starts from zero. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
