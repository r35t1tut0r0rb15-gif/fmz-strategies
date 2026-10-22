# #458059 Weighted Moving Average and Relative Strength Index Crossover Strategy with Risk Management Optimization System -> `fmz_458059_wma7_9_cross_up_rsi40_point_bracket_long`

- FMZ source id: 458059 (lineage).
- Source: https://www.fmz.com/strategy/458059 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:07:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of 42000 |
| 2 | PASS | WMA cross-ups in a weak RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.000476, 0.01] x `tp_frac` [0.000952, 0.02]: **4 trials**; the WMA and RSI settings fixed.

## Ambiguities resolved

- Points as fractions of 42000. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
