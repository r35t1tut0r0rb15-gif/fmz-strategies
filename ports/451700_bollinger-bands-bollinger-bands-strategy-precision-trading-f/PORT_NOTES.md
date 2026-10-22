# #451700 Bollinger-Bands-布林带策略精准交易实现最大收益-Bollinger-Bands-Strategy-Precision-Trading-for-Maximum-Gains -> `fmz_451700_bollinger_lower_basis_cross_reversal`

- FMZ source id: 451700 (lineage).
- Source: https://www.fmz.com/strategy/451700 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:32:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band and basis crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
