# #429464 Dual Moving Average Crossover Strategy -> `fmz_429464_sma_diff_cross_long`

- FMZ source id: 429464 (lineage).
- Source: https://www.fmz.com/strategy/429464 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-17 13:54:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A cross of two series in the same units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [50, 20] x `len2` [100, 200]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
