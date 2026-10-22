# #478695 基于移动平均线和Outside-Bar模式的双重趋势确认交易策略-Dual-Trend-Confirmation-Trading-Strategy-Based-on-Moving-Averages-and-Outside-Bar-Pattern -> `fmz_478695_outside_bar_ema5_ema9shift_height_bracket_reversal`

- FMZ source id: 478695 (lineage).
- Source: https://www.fmz.com/strategy/478695 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:39:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Outside bars beyond two EMAs with a bar-height bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_ratio` [0.5, 1.0] x `sl_ratio` [1.0, 0.5]: **4 trials**; EMA 5 / 9, shift 1.

## Ambiguities resolved

- The stop-and-reverse block fires only on a zero-range bar and is not ported. Repeat-signal re-sends not followed.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
