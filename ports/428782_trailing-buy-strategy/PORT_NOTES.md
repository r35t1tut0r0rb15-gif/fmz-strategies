# #428782 Trailing Buy Strategy -> `fmz_428782_sma_cross_trailing_buy`

- FMZ source id: 428782 (lineage).
- Source: https://www.fmz.com/strategy/428782 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-09 14:53:02). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the buy level is a close-checked condition. |
| 2 | PASS | Percentages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`deviation` [0.04, 0.02] x `fast` [21, 10]: **4 trials**; slow 49 and source high fixed.

## Ambiguities resolved

- barssince with nz 999999 as written; the level restarts from low x (1 + deviation) on the cross bar.
- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
