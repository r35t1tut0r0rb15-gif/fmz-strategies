# #458069 Precision Trading Strategy and Risk Management System Based on SuperTrend Indicator -> `fmz_458069_supertrend_line_cross_1pct_bracket_reversal`

- FMZ source id: 458069 (lineage).
- Source: https://www.fmz.com/strategy/458069 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:58:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | Supertrend line crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 14] x `factor` [3.0, 2.0] x `bracket` [0.01, 0.03]: **8 trials**.

## Ambiguities resolved

- Bracket as 1 % of the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
