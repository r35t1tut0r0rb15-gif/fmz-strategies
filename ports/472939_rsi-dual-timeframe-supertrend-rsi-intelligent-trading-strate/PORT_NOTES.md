# #472939 双时间周期超趋势RSI智能交易策略-Dual-Timeframe-Supertrend-RSI-Intelligent-Trading-Strategy -> `fmz_472939_supertrend_direction_rsi60_40_reversal`

- FMZ source id: 472939 (lineage).
- Source: https://www.fmz.com/strategy/472939 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 11:18:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend direction with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 14]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- Direction 1 is Pine's down trend (as written); the 60-minute request is the chart itself. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
