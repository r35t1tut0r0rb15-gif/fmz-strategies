# #472936 Multi EMA Trend Momentum Recognition and Stop Loss Trading System -> `fmz_472936_four_ema_stack_state_2pct_stop_reversal`

- FMZ source id: 472936 (lineage).
- Source: https://www.fmz.com/strategy/472936 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 11:09:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price stop as a fixed fraction |
| 2 | PASS | Stacked EMA states with a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.02, 0.05]: **2 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Stop from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
