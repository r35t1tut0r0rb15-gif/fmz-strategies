# #477528 Adaptive Channel Breakout Strategy with Dynamic Support and Resistance Trading System -> `fmz_477528_near_20bar_low_pct_bracket_long`

- FMZ source id: 477528 (lineage).
- Source: https://www.fmz.com/strategy/477528 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:40:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | Near-support buys with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `tp_pct` [0.03, 0.06]: **4 trials**; within 1 %, stop 1.5 %.

## Ambiguities resolved

- State entry repeats while it holds. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`coarse_bar_stop`
