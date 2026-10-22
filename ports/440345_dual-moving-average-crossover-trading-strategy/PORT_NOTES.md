# #440345 Dual Moving Average Crossover Trading Strategy -> `fmz_440345_three_timeframe_ema_crossings`

- FMZ source id: 440345 (lineage).
- Source: https://www.fmz.com/strategy/440345 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-29 15:11:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed bars |
| 2 | PASS | EMA crossings across timeframes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [10, 20] x `ma23_len` [200, 100]: **4 trials**; the same length for MA2 and MA3; timeframes fixed.

## Ambiguities resolved

- Higher-timeframe EMAs from the last completed bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
