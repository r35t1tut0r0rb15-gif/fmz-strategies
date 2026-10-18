# #435837 Dual Factor Mean Reversion Tracking Strategy -> `fmz_435837_reversal_123_keltner_channel`

- FMZ source id: 435837 (lineage).
- Source: https://www.fmz.com/strategy/435837 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 11:09:20). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a channel state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `n_period` [10, 20]: **4 trials**; stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
