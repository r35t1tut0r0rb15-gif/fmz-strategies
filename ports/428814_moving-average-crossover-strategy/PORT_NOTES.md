# #428814 Moving Average Crossover Strategy -> `fmz_428814_sma10_20_cross_trend_long`

- FMZ source id: 428814 (lineage).
- Source: https://www.fmz.com/strategy/428814 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 17:03:23). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [10, 5] x `ma2` [20, 40]: **4 trials**; trend SMA 200 fixed.

## Ambiguities resolved

- Default branch only. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
