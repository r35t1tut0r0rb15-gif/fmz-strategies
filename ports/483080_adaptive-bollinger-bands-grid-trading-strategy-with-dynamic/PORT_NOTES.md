# #483080 自适应布林网格交易策略-Adaptive-Bollinger-Bands-Grid-Trading-Strategy-with-Dynamic-Level-Adjustment -> `fmz_483080_bollinger_grid_level_crosses_1d`

- FMZ source id: 483080 (lineage).
- Source: https://www.fmz.com/strategy/483080 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:04:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and percentage offsets. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the grid ids are not adds (one position). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`grid_pct` [1.0, 2.0] x `mult` [2.0, 2.5]: **4 trials**; defaults 1 / 2 (the source's); BB 20 and 4 levels fixed.

## Ambiguities resolved

- One position (pyramiding 1): the grid entry ids add nothing while held; entries reverse. A long and a short entry on
  one bar: the later short wins.
- The crosses inside the `for` loop share one call site, so their previous-bar values are those of the previous bar's
  last iteration (level 3), as written; the level-0 crosses are ordinary.
- REVERSAL INTENDED; no exits or stops. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
