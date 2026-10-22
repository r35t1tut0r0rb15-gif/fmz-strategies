# #442959 Trend Tracking Strategy Based on Moving Average -> `fmz_442959_close_sma500_cross_reversal`

- FMZ source id: 442959 (lineage).
- Source: https://www.fmz.com/strategy/442959 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:29:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_period` [500, 200]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
