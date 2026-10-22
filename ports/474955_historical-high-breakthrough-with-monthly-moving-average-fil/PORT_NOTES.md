# #474955 Historical High Breakthrough with Monthly Moving Average Filter Trend Following Strategy -> `fmz_474955_all_time_high_close_break_monthly_sma8_exit_long`

- FMZ source id: 474955 (lineage).
- Source: https://www.fmz.com/strategy/474955 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:25:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed monthly values |
| 2 | PASS | All-time-high breakouts with a monthly filter exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [8, 4]: **2 trials**.

## Ambiguities resolved

- The all-time high counts from the first loaded bar; the SMA 8 over daily samples of the monthly close, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
