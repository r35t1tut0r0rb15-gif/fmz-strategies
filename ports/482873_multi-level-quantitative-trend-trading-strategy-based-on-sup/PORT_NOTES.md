# #482873 基于支撑阻力位突破和回测的多级量化趋势交易策略-Multi-Level-Quantitative-Trend-Trading-Strategy-Based-on-Support-Resistance-Breakout-and-Retest -> `fmz_482873_pivot_break_retest_reversal_1d`

- FMZ source id: 482873 (lineage).
- Source: https://www.fmz.com/strategy/482873 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:00:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Pivot levels and a percentage tolerance. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_bars` [3, 5] x `tolerance` [0.005, 0.01]: **4 trials**; defaults 3 / 0.005 (the source's; left = right bars).

## Ambiguities resolved

- Pivots are strict extremes confirmed later (as #430850). Break and retest may fall on one bar; one entry per level.
- REVERSAL INTENDED; no exits or stops; the later short wins over a long on one bar. "4hr" is a label.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
