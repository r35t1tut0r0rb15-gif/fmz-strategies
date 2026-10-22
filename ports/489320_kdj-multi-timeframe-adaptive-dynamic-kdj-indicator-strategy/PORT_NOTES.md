# #489320 多重时间框架自适应动态KDJ指标策略-Multi-Timeframe-Adaptive-Dynamic-KDJ-Indicator-Strategy -> `fmz_489320_mtf_adaptive_kdj_cross_anticipate_extreme_reversal`

- FMZ source id: 489320 (lineage).
- Source: https://www.fmz.com/strategy/489320 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 15:13:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent stop pending |
| 2 | PASS | Multi-frame adaptive KDJ crossings and anticipations |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smoothingLength` [5, 10] x `trendLength` [40, 20]: **4 trials**; weights 0.5 / 0.33 / 0.17, levels 22 / 78.

## Ambiguities resolved

- Lower frames are each day's last bar; the per-bar stop is pending. REVERSAL INTENDED. FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic"`.

## Marks

`trailing_stop_pending`
