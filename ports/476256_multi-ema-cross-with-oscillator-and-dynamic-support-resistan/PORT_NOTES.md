# #476256 Multi EMA Cross with Oscillator and Dynamic Support Resistance Trading Strategy -> `fmz_476256_ema4_cross_ema9_ema18_atr_filter_ema_stop_reversal`

- FMZ source id: 476256 (lineage).
- Source: https://www.fmz.com/strategy/476256 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:45:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar EMA stop as a fraction of the fill |
| 2 | PASS | Triple EMA crossings with an ATR distance filter and an EMA stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [14, 7] x `atr_mult` [1.0, 0.5]: **4 trials**; EMA 4 / 9 / 18 fixed.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
