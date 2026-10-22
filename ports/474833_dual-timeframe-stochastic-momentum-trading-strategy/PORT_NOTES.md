# #474833 Dual Timeframe Stochastic Momentum Trading Strategy -> `fmz_474833_stoch14_kd_cross_extremes_pct_bracket_reversal`

- FMZ source id: 474833 (lineage).
- Source: https://www.fmz.com/strategy/474833 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:19:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Stochastic crossings at the extremes with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `tp_pct` [2.0, 4.0] x `sl_pct` [1.0, 2.0]: **8 trials**; levels 80 / 20.

## Ambiguities resolved

- Repeat-signal re-sends not followed (trailing_stop_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
