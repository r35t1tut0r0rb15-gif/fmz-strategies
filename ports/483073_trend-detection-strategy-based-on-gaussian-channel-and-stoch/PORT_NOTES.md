# #483073 Trend Detection Strategy Based on Gaussian Channel and Stochastic RSI Filter -> `fmz_483073_smoothed_close_2pct_channel_stoch_extreme_reversal`

- FMZ source id: 483073 (lineage).
- Source: https://www.fmz.com/strategy/483073 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:42:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed percent channel crossings with Stochastic extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`input_length` [100, 50] x `input_mult` [2.0, 1.0]: **4 trials**; Stochastic 14 / 3 / 3, levels 80 / 20.

## Ambiguities resolved

- The date window is dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
