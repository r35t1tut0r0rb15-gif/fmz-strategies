# #454144 RSI趋势策略-RSI-Trend-Strategy -> `fmz_454144_rsi9_dip_from_flat_stop_time_exit_long`

- FMZ source id: 454144 (lineage).
- Source: https://www.fmz.com/strategy/454144 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:28:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop as a fixed fraction; the time exit as a close test |
| 2 | PASS | RSI dips with RSI and time exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The order size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [9, 14] x `sl_pct` [0.01, 0.03] x `max_hours` [24, 48]: **8 trials**; the levels fixed.

## Ambiguities resolved

- Time exit on bar open times (strictly over 24 h). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
