# #474964 Dual EMA Stochastic Trend Following Trading Strategy -> `fmz_474964_ema50_150_trend_stoch_cross_swing_bracket_reversal`

- FMZ source id: 474964 (lineage).
- Source: https://www.fmz.com/strategy/474964 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:48:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Trend stochastic crossings with a swing bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [150, 100]: **4 trials**; stochastic fixed.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
