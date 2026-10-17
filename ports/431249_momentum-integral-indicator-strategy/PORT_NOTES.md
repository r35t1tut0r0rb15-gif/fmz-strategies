# #431249 Momentum Integral Indicator Strategy -> `fmz_431249_sma_deviation_integral`

- FMZ source id: 431249 (lineage).
- Source: https://www.fmz.com/strategy/431249 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-06 14:40:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The sign of a sum of deviations from an SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG431249. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [170, 85] x `terms` [18, 9]: **4 trials** (the sum has terms + 1 values).

## Ambiguities resolved

- 19-term sum as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
