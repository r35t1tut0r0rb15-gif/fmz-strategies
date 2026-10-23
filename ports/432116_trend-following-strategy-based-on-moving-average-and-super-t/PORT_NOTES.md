# #432116 Trend Following Strategy Based on Moving Average and Super Trend -> `fmz_432116_atr50_supertrend_line_cross_daily_reversal`

- FMZ source id: 432116 (lineage).
- Source: https://www.fmz.com/strategy/432116 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-14 16:23:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing-line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_period` [50, 20] x `st_mult` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Same-timeframe security() read as the chart's bars. Volume-weighted MA and VHMA are plot-only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
