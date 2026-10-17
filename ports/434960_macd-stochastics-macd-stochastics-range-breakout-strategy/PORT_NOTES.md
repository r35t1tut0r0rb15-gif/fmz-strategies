# #434960 MACD-Stochastics波段震荡突破策略MACD-Stochastics-Range-Breakout-Strategy -> `fmz_434960_slow_macd_stoch_cross_tp`

- FMZ source id: 434960 (lineage).
- Source: https://www.fmz.com/strategy/434960 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 11:48:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent target |
| 2 | PASS | MACD side and stochastic crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_len` [14, 7] x `tp_pct` [0.03, 0.06]: **4 trials**; MACD 180 / 390 / 135 and the 30 / 70 levels fixed.

## Ambiguities resolved

- Target only, fixed at the fill. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
