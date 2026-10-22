# #483794 Multi Indicator Momentum Wave Trading Strategy -> `fmz_483794_macd12_26_20_hist_zero_cross_level_exit_reversal`

- FMZ source id: 483794 (lineage).
- Source: https://www.fmz.com/strategy/483794 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-26 10:30:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Histogram exit levels read as fractions of the close at ETH 3000 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`signal_length` [20, 9] x `long_exit_frac` [3.667e-03, 6.0e-03]: **4 trials**; MACD 12 / 26, short exit -3.0e-03 x close.

## Ambiguities resolved

- The exit levels are read at ETH 3000. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
