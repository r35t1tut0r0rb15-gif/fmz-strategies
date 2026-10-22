# #453665 TSI交叉策略-TSI-Crossover-Strategy -> `fmz_453665_tsi_extreme_cross_ny_session_reversal`

- FMZ source id: 453665 (lineage).
- Source: https://www.fmz.com/strategy/453665 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 16:36:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TSI extreme crossings in a session |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tsi_long` [8, 25] x `tsi_short` [8, 13] x `gap_bars` [12, 6]: **8 trials**; the signal 3 and the lines fixed.

## Ambiguities resolved

- Session in New York time on the bar open. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
