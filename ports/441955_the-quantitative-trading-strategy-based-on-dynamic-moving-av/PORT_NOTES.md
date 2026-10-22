# #441955 The Quantitative Trading Strategy Based on Dynamic Moving Average Breakthrough Entry -> `fmz_441955_monday_dip_under_hma115_wednesday_exit_long`

- FMZ source id: 441955 (lineage).
- Source: https://www.fmz.com/strategy/441955 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 09:53:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weekday window and HMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [115, 55]: **2 trials**.

## Ambiguities resolved

- UTC weekday and window; the exit bracket names a non-existent entry and is not ported. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
