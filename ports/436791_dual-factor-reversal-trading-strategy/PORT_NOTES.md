# #436791 Dual factor Reversal Trading Strategy -> `fmz_436791_reversal123_bandpass_trend_combo`

- FMZ source id: 436791 (lineage).
- Source: https://www.fmz.com/strategy/436791 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 17:22:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and band-pass sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435522. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_ett` [20, 40]: **4 trials**; K smoothing 1, D 3, level 50, delta 0.5 and trigger 0 fixed; reverse off.

## Ambiguities resolved

- 3.1415 as pi as written; 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
