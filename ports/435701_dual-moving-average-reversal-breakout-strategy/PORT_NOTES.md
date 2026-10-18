# #435701 Dual Moving Average Reversal Breakout Strategy -> `fmz_435701_reversal_123_price_ma_distance`

- FMZ source id: 435701 (lineage).
- Source: https://www.fmz.com/strategy/435701 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 10:24:08). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and a percent distance to an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length_dbp` [14, 28]: **4 trials**; stochastic 14 / 1 / 3, level 50 and the zones fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
