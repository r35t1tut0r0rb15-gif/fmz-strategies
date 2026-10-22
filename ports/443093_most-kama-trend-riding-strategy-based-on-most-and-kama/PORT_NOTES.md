# #443093 基于MOST和KAMA的趋势跟踪策略Trend-Riding-Strategy-Based-on-MOST-and-KAMA -> `fmz_443093_most_kama3_band_cross_long`

- FMZ source id: 443093 (lineage).
- Source: https://www.fmz.com/strategy/443093 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 11:04:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | KAMA vs MOST band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [3, 10] x `percent` [3.3, 6.0]: **4 trials**.

## Ambiguities resolved

- KAMA nz seed as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
