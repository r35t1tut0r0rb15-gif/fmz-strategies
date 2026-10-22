# #478721 Multi Indicator Dynamic Trend Detection and Risk Management Trading Strategy -> `fmz_478721_rsi14_extreme_stoch_turn_pct_bracket_level_gate_reversal`

- FMZ source id: 478721 (lineage).
- Source: https://www.fmz.com/strategy/478721 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 15:55:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | RSI extremes with a turning stochastic and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.01, 0.03] x `sl_pct` [0.05, 0.02]: **4 trials**; RSI 14, stochastic 14, chop 14.

## Ambiguities resolved

- The "chop" filter almost always passes, as written; level flags gate re-entries. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
