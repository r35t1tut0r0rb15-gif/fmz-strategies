# #482787 多重技术指标趋势反转量化交易策略结合动态SAR参数优化系统-Multi-Technical-Indicator-Trend-Reversal-Quantitative-Trading-Strategy-with-Dynamic-SAR-Parameter-Optimization-System -> `fmz_482787_sar_flip_pivot5_trend_fractal2_reversal`

- FMZ source id: 482787 (lineage).
- Source: https://www.fmz.com/strategy/482787 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 11:03:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR flips with pivot-trend and fractal filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zigzag_depth` [5, 10] x `sar_start` [0.02, 0.01]: **4 trials**; fractals 2 / 2, increment 0.2, maximum 0.02 as written.

## Ambiguities resolved

- The SAR arguments are passed in the source's order (constant factor). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
