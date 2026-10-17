# #482787 多重技术指标趋势反转量化交易策略结合动态SAR参数优化系统-Multi-Technical-Indicator-Trend-Reversal-Quantitative-Trading-Strategy-with-Dynamic-SAR-Parameter-Optimization-System -> `fmz_482787_sar_flip_pivot_side_fractal`

- FMZ source id: 482787 (lineage).
- Source: https://www.fmz.com/strategy/482787 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 11:03:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The parabolic SAR and confirmed pivots. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_max` [0.02, 0.2] x `depth` [5, 10]: **4 trials**; defaults 0.02 / 5 (the source's); SAR start 0.02, increment
0.2 and fractals 2 / 2 fixed.

## Ambiguities resolved

- `ta.sar(0.02, 0.2, 0.02)` caps the acceleration at 0.02 (a constant factor), as written; 0.2 is the variant.
- Pivots strict on both sides, confirmed `depth` bars later (as #430850). The deviation input is unused.
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
