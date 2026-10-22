# #458250 Lorenzian Classification Multi Timeframe Target Strategy -> `fmz_458250_lorenzian_line_cross_pct_target_stop_tests_reversal`

- FMZ source id: 458250 (lineage).
- Source: https://www.fmz.com/strategy/458250 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:49:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target and stop are bar-close tests |
| 2 | PASS | Smoothed-line crossings with a percent target and stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `lookback` [3, 5] x `target_pct` [0.015, 0.03]: **8 trials**.

## Ambiguities resolved

- Levels cleared as written on a reversal bar; exits are bar-close tests. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
