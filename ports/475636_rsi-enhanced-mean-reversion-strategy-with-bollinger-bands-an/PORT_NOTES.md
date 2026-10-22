# #475636 布林带RSI均值回归增强型量化策略-Enhanced-Mean-Reversion-Strategy-with-Bollinger-Bands-and-RSI-Integration -> `fmz_475636_bb20_rsi30_70_extreme_reversal`

- FMZ source id: 475636 (lineage).
- Source: https://www.fmz.com/strategy/475636 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 17:03:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band / RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `std_dev` [2.0, 2.5]: **4 trials**; RSI levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
