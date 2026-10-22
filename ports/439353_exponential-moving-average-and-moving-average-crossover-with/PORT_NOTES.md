# #439353 Exponential Moving Average and Moving Average Crossover with Close Strategy -> `fmz_439353_ema9_sma20_side_cross_close`

- FMZ source id: 439353 (lineage).
- Source: https://www.fmz.com/strategy/439353 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:50:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average sides and crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ema` [9, 20] x `length_ma` [20, 50]: **4 trials**.

## Ambiguities resolved

- The final close_all leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
