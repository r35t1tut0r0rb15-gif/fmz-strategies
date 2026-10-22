# #473405 Triple EMA Trend Following Quantitative Trading Strategy -> `fmz_473405_ema10_30_130_slope_cross_long`

- FMZ source id: 473405 (lineage).
- Source: https://www.fmz.com/strategy/473405 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:54:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with slope filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `mid` [30, 50] x `slow` [130, 200]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
