# #433442 Range Breakthrough Dual Moving Average Filtering Strategy -> `fmz_433442_range_filter_macd_burst`

- FMZ source id: 433442 (lineage).
- Source: https://www.fmz.com/strategy/433442 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 17:03:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A range filter and a slope / width ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 5 stacking stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [100, 50] x `sensitivity` [150, 75]: **4 trials**; multiplier 3, MACD 20 / 40 and BB 20 / 2 fixed.

## Ambiguities resolved

- Net position ported (pyramiding stacking is sizing). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "range_filter_trend"`.

## Marks

`none`
