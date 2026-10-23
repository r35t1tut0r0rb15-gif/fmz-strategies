# #453279 Smooth Moving Average Stop Loss Take Profit Strategy with Trend Filter and Exception Exit -> `fmz_453279_quiet_dip_under_sma200_late_armed_stop_1h_long_only`

- FMZ source id: 453279 (lineage).
- Source: https://www.fmz.com/strategy/453279 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:54:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; late-armed stop followed in the signals |
| 2 | PASS | Quiet-market dips under the SMA 200 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_percent` [5.0, 2.0] x `wait_bars` [3, 6]: **4 trials**; TP x 1.5, SMA 200, RSI 14.

## Ambiguities resolved

- Late-armed stop in the signals; the +150 % target and the exit condition never act. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback_time_exit"`.

## Marks

`trailing_stop_pending`
