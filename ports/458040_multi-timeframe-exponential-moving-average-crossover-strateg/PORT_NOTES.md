# #458040 Multi Timeframe Exponential Moving Average Crossover Strategy with Risk Reward Optimization -> `fmz_458040_ema21_recross_4h_ema_filter_reversal`

- FMZ source id: 458040 (lineage).
- Source: https://www.fmz.com/strategy/458040 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:20:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 4-hour EMAs from completed bars; the late-armed bracket pending (mark) |
| 2 | PASS | Trend pullback re-crosses with a higher-time-frame filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the 4-hour lengths follow the same inputs.

## Ambiguities resolved

- 4-hour EMAs from the last completed 4-hour bar; late-armed bracket pending. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`trailing_stop_pending`
