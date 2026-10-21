# #437658 Dual Moving Average Crossover Reverse Trend Tracking Strategy -> `fmz_437658_reversal123_ma_ema_combo`

- FMZ source id: 437658 (lineage).
- Source: https://www.fmz.com/strategy/437658 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:48:15). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and an average comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_ma` [10, 20]: **4 trials**; K smoothing 1, D 3, level 50 and EMA 10 fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
