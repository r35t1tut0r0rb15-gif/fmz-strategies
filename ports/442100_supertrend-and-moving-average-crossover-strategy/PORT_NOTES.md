# #442100 Supertrend and Moving Average Crossover Strategy -> `fmz_442100_ema10_sma20_side_supertrend_direction`

- FMZ source id: 442100 (lineage).
- Source: https://www.fmz.com/strategy/442100 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 11:56:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA side and SuperTrend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [10, 14] x `factor` [3.0, 2.0]: **4 trials**; EMA 10 / SMA 20 fixed.

## Ambiguities resolved

- Direction sign as written (long with direction 1). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
