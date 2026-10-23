# #434177 Adaptive Volatility Breakout Trading Strategy -> `fmz_434177_fractal_bottom_gap_under_volume_fractal_level_long`

- FMZ source id: 434177 (lineage).
- Source: https://www.fmz.com/strategy/434177 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-04 14:34:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal reversal entries under the last volume fractal level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 10000 cash per lot, pyramiding 1, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap_pct` [0.0001, 0.002] x `vol_ma` [2, 5]: **4 trials**.

## Ambiguities resolved

- Bottom_1 / Top_1 = the current fractal levels (save loops). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "fractal"`.

## Marks

`none`
