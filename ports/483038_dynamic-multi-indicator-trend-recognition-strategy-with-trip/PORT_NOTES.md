# #483038 Dynamic Multi Indicator Trend Recognition Strategy with Triple Sync Analysis -> `fmz_483038_adx_stochrsi_cci_snake_range_20_80_cross_reversal`

- FMZ source id: 483038 (lineage).
- Source: https://www.fmz.com/strategy/483038 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:31:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Composite oscillator against its own range levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 10] x `dyn_len` [100, 50]: **4 trials**; levels 20 % / 80 %.

## Ambiguities resolved

- The hand-built ADX is kept as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
