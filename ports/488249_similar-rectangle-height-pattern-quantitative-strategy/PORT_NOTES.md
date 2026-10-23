# #488249 Similar Rectangle Height Pattern Quantitative Strategy -> `fmz_488249_similar_rectangle_heights_pattern_bracket_reversal`

- FMZ source id: 488249 (lineage).
- Source: https://www.fmz.com/strategy/488249 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 11:44:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent-of-average bracket at the signal close as fractions of the fill |
| 2 | PASS | Range-height pattern matching |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`primary_pct` [5.0, 3.0] x `corr_pct` [2.2, 1.5]: **4 trials**; lookback 45, widths 5 .. 14, RSI 23 (50 / 55).

## Ambiguities resolved

- A "pattern" is effectively a 5-bar run between the window's ends. Volume off by default. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "chart_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
