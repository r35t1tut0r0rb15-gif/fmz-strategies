# #426808 Enhanced Moving Average Convergence Trend Strategy -> `fmz_426808_macd_of_histogram_long`

- Source: https://www.fmz.com/strategy/426808 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 16:46:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [26, 34] x `signal` [9, 5]: **8 trials**, defaults 12 / 26 / 9 (the source's).

## Ambiguities resolved

- inTimeRange hard-coded true; long only.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
