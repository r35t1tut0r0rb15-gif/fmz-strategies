# #360018 Get your trend -> `fmz_360018_sma_stack_volume_adx_mesa_cloud_pivot_trend_long`

- FMZ source id: 360018 (lineage).
- Source: https://www.fmz.com/strategy/360018 (PineScript v4, author 发明者量化, FMZ last
  modified 2022-05-07 13:52:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA stack with volume, ADX and adaptive-cloud confirmation; trend-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_f` [1.8, 1.2] x `th` [15.0, 25.0]: **4 trials**; SMA 5 / 15 / 25, ADX 20, pivots 15, cloud 30.

## Ambiguities resolved

- MESA / KAMA recursions with nz() as written; pivot-centre band as written. Volume = broker tick volume.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
