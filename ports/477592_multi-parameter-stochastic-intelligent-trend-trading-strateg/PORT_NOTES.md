# #477592 Multi Parameter Stochastic Intelligent Trend Trading Strategy -> `fmz_477592_stoch14_level_cross_pct_bracket_reversal`

- FMZ source id: 477592 (lineage).
- Source: https://www.fmz.com/strategy/477592 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 16:09:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Stochastic level crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop percentage and R:R stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [1.0, 4.0, 8.0] x `stop_pct` [0.01, 0.02]: **6 trials**; stochastic 14 / 5, levels 15 / 40 / 93.

## Ambiguities resolved

- Each position keeps its opening bracket. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
