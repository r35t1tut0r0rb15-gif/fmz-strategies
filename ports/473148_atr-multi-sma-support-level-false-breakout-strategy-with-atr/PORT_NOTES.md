# #473148 多重均线支撑位假突破策略结合ATR止损系统-Multi-SMA-Support-Level-False-Breakout-Strategy-with-ATR-Stop-Loss-System -> `fmz_473148_pivot_support_false_break_atr_stop_swing_target_long`

- FMZ source id: 473148 (lineage).
- Source: https://www.fmz.com/strategy/473148 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:17:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | False breaks of a pivot support in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `atr_mult` [1.0, 2.0]: **4 trials**; the SMA lengths fixed.

## Ambiguities resolved

- Opening levels kept on repeat signals (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
