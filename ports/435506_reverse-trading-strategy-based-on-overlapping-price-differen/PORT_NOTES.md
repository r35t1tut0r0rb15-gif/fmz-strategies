# #435506 Reverse Trading Strategy Based on Overlapping Price Differentials -> `fmz_435506_price_change_reversal_bracket`

- FMZ source id: 435506 (lineage).
- Source: https://www.fmz.com/strategy/435506 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-15 15:47:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit move and tick bracket -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial capital input stored; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bracket` [0.0095, 0.02] x `min_move` [0.0005, 0.005]: **4 trials**; sum 30 and signal 15 fixed.

## Ambiguities resolved

- Price-unit move and tick bracket -> fractions; bracket fixed at the fill. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
