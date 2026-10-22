# #477533 Dual EMA Stochastic Oscillator System A Quantitative Trading Model Combining Trend Following and Momentum -> `fmz_477533_stoch14_band_cross_ema20_50_trend_pct_bracket_reversal`

- FMZ source id: 477533 (lineage).
- Source: https://www.fmz.com/strategy/477533 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 11:48:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Stochastic band crossings on the EMA trend side with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_k` [14, 21] x `rr` [2.0, 3.0]: **4 trials**; bands 15 / 85, stop 1 %.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
