# #436860 Reversal Dual Moving Average Crossover Strategy -> `fmz_436860_hma_cross_turning_point_exit`

- FMZ source id: 436860 (lineage).
- Source: https://www.fmz.com/strategy/436860 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-28 12:00:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing and percent slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430020. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [5, 9] x `ma2` [7, 14]: **4 trials**; both types HMA, look back 1 and slope 0.02 % fixed.

## Ambiguities resolved

- VWMA type left out (volume); call-order fills. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
