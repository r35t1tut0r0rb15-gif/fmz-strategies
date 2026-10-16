# #429484 Momentum Tracking Strategy Based on Indicator Integration -> `fmz_429484_integrated_sma_distance`

- FMZ source id: 429484 (lineage).
- Source: https://www.fmz.com/strategy/429484 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-17 15:26:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The sign of a sum only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the off-by-default exits stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [170, 100] x `terms` [30, 15]: **4 trials**.

## Ambiguities resolved

- Off-by-default exits not ported. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
