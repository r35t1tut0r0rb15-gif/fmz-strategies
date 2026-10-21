# #437515 Dual Reversal High Low Strategy -> `fmz_437515_reversal123_high_ema_combo`

- FMZ source id: 437515 (lineage).
- Source: https://www.fmz.com/strategy/437515 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 13:56:04). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a high-over-EMA sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_hema` [13, 26]: **4 trials**; K smoothing 1, D 3 and level 50 fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
