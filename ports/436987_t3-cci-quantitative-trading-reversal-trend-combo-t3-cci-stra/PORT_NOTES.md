# #436987 量化交易反转趋势串并T3-CCI策略Quantitative-Trading-Reversal-Trend-Combo-T3-CCI-Strategy -> `fmz_436987_reversal123_t3_cci_combo`

- FMZ source id: 436987 (lineage).
- Source: https://www.fmz.com/strategy/436987 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 10:44:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and CCI sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `cci_period` [14, 20]: **4 trials**; K smoothing 1, D 3, level 50, T3 5 and b 0.618 fixed; reverse off.

## Ambiguities resolved

- nz() restarts as written; 123 test as written; state 0 closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
