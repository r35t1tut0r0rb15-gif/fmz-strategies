# #440535 Crossover Strategy of Moving Average Lines and Resistance Level Breakout -> `fmz_440535_ma_stack_breakout_wait_15pct_target_close_stop_1h_long_only`

- FMZ source id: 440535 (lineage).
- Source: https://www.fmz.com/strategy/440535 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 14:34:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed target from the fill; bar-close stop in the signals |
| 2 | PASS | Trend-filtered breakouts with a post-exit wait |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profit_target` [0.15, 0.05] x `wait_candles` [10, 20]: **4 trials**; stop 3 %, SMA 20 / 44 / 100.

## Ambiguities resolved

- Target armed at the fill; low-based stop at the bar close. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
