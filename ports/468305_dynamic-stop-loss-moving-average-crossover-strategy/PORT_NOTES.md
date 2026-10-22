# #468305 Dynamic Stop Loss Moving Average Crossover Strategy -> `fmz_468305_ema9_21_cross_swing_stop_3r_target_reversal`

- FMZ source id: 468305 (lineage).
- Source: https://www.fmz.com/strategy/468305 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 14:47:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | EMA crossings with swing stops and 1:3 targets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50] x `rr` [3.0, 2.0]: **8 trials**; the 5-bar swing fixed.

## Ambiguities resolved

- No trail (offset only); marketable levels closed one bar late. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
