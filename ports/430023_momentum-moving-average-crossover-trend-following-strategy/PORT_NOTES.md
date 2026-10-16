# #430023 Momentum Moving Average Crossover Trend Following Strategy -> `fmz_430023_hma_cross_turning_exits`

- FMZ source id: 430023 (lineage).
- Source: https://www.fmz.com/strategy/430023 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-24 12:31:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages of the open, ADX and a percentage slope. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [5, 9] x `adx_threshold` [20, 25]: **4 trials**; HMA 2 = ma1 + 2, ADX 14 / 14 and the 0.02 % slope fixed.

## Ambiguities resolved

- Close and entry on one bar: the close acts only on a position held from before the bar and not reversed by it.
- Default HMA only. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
