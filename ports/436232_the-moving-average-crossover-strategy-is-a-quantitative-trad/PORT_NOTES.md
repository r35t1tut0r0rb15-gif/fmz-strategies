# #436232 The moving average crossover strategy is a quantitative trading strategy -> `fmz_436232_double_sma_cross_reversal`

- FMZ source id: 436232 (lineage).
- Source: https://www.fmz.com/strategy/436232 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 13:28:01). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Stop orders sent on the reversing bar: no effect |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG436232. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [45, 30]: **4 trials**.

## Ambiguities resolved

- Same-bar double cross; stop orders on the reversing bar not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
