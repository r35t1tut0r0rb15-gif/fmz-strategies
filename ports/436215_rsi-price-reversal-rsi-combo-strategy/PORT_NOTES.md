# #436215 价格反转RSI组合策略Price-Reversal-RSI-Combo-Strategy -> `fmz_436215_reversal_123_rsi_momentum`

- FMZ source id: 436215 (lineage).
- Source: https://www.fmz.com/strategy/436215 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 11:53:11). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pattern state and an RSI state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length_rsi` [12, 14]: **4 trials**; levels 30 / 70, stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- Persistent states combined; disagreement closes. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
