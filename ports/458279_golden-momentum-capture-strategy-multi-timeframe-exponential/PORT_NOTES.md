# #458279 Golden Momentum Capture Strategy Multi Timeframe Exponential Moving Average Crossover System -> `fmz_458279_ema9_26_cross_ema55_side_reversal`

- FMZ source id: 458279 (lineage).
- Source: https://www.fmz.com/strategy/458279 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 15:00:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [26, 21] x `trend` [55, 100]: **8 trials**.

## Ambiguities resolved

- Chart time frame for every EMA (default inputs). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
