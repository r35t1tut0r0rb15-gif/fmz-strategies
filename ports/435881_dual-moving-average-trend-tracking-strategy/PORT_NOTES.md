# #435881 Dual Moving Average Trend Tracking Strategy -> `fmz_435881_noro_trendma`

- FMZ source id: 435881 (lineage).
- Source: https://www.fmz.com/strategy/435881 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 14:49:52). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average slopes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 50] x `type` ["SMA", "EMA"]: **8 trials**.

## Ambiguities resolved

- Slopes of both averages; type in the grid. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
