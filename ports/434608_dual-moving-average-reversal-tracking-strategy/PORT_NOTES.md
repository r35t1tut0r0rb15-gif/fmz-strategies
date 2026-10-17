# #434608 Dual Moving Average Reversal Tracking Strategy -> `fmz_434608_prev_day_close_sma_side`

- FMZ source id: 434608 (lineage).
- Source: https://www.fmz.com/strategy/434608 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 17:40:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Price against a prior-day level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 50] x `reverse` [False, True]: **4 trials**.

## Ambiguities resolved

- Chart-bar SMA of the previous broker day's close, as written. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
