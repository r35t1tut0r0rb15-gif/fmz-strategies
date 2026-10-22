# #440090 Price Crossing Moving Average Trend Following Strategy -> `fmz_440090_close_hma100_cross`

- FMZ source id: 440090 (lineage).
- Source: https://www.fmz.com/strategy/440090 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 15:18:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / HMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [100, 50] x `tol` [0.0, 0.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
