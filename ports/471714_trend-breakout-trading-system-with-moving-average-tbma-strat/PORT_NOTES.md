# #471714 Trend Breakout Trading System with Moving Average TBMA Strategy -> `fmz_471714_close_over_sma20_low7_stop_2r_target_long`

- FMZ source id: 471714 (lineage).
- Source: https://www.fmz.com/strategy/471714 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:24:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | SMA breakouts with a swing-low stop and 2:1 target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_len` [20, 50] x `low_len` [7, 14] x `rr` [2.0, 3.0]: **8 trials**.

## Ambiguities resolved

- Opening levels kept on repeat breakouts (trailing_stop_pending); marketable levels closed one bar late. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
