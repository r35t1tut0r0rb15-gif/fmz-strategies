# #443243 基于HullMA百分比带的量化交易策略Quant-Trading-Strategy-Based-on-HullMA-Percentage-Bands -> `fmz_443243_hull9_percent_band_cross_long_5d`

- FMZ source id: 443243 (lineage).
- Source: https://www.fmz.com/strategy/443243 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-03-01 12:16:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull percentage bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 20] x `band1` [3.0, 2.0]: **4 trials** (the outer band is twice the inner).

## Ambiguities resolved

- Same-crossing entry and close as written. Long only. FREQ = "5D" (five broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
