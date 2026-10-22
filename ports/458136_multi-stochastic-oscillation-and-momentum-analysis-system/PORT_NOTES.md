# #458136 Multi Stochastic Oscillation and Momentum Analysis System -> `fmz_458136_stacked_smoothed_stochastics_reversal`

- FMZ source id: 458136 (lineage).
- Source: https://www.fmz.com/strategy/458136 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 11:04:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked smoothed stochastics |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21]: **2 trials**; the smoothing ladder fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
