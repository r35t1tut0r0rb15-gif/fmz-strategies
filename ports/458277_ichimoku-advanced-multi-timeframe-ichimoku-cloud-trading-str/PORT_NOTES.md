# #458277 基于多维度动态云图的Ichimoku高级多周期交易策略-Advanced-Multi-Timeframe-Ichimoku-Cloud-Trading-Strategy-with-Dynamic-Multidimensional-Analysis -> `fmz_458277_tenkan_kijun_cross_above_cloud_long`

- FMZ source id: 458277 (lineage).
- Source: https://www.fmz.com/strategy/458277 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:54:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Tenkan / Kijun crossings with a cloud filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 7] x `kijun` [26, 22] x `span_b` [52, 44]: **8 trials**.

## Ambiguities resolved

- Spans undisplaced (as written); the unused stop / target not ported. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
