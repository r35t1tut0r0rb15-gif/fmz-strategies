# #436100 Trend Trading Strategy Based on Dynamic Moving Average -> `fmz_436100_hull_slope_long_only`

- FMZ source id: 436100 (lineage).
- Source: https://www.fmz.com/strategy/436100 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 11:33:50). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull average slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND365727. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 100] x `mode` ["Hma", "Ehma", "Thma"]: **6 trials**.

## Ambiguities resolved

- Short entries forbidden: the falling Hull closes the long. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
