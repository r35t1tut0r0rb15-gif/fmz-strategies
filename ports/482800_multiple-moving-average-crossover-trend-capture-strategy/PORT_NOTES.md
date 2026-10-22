# #482800 Multiple Moving Average Crossover Trend Capture Strategy -> `fmz_482800_close_sma2_cross_sma4_reversal`

- FMZ source id: 482800 (lineage).
- Source: https://www.fmz.com/strategy/482800 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 11:31:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`t_length` [2, 3] x `f_length` [4, 8]: **4 trials**; SMA 1 (the close).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
