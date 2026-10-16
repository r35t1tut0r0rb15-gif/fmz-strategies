# #427593 SMA Moving Average Crossover Strategy -> `fmz_427593_sma_10_100_cross`

- FMZ source id: 427593 (lineage).
- Source: https://www.fmz.com/strategy/427593 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-22 14:40:03). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [10, 20] x `ma2` [100, 50] x `ma_type` [1 SMA, 2 EMA]: **8 trials**; defaults 10 / 100 / SMA (the source's).

## Ambiguities resolved

- `security(..., timeframe.period, close)` is the close itself. REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
