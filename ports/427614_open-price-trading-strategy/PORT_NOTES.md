# #427614 Open Price Trading Strategy -> `fmz_427614_open_close_ratio_mean`

- FMZ source id: 427614 (lineage).
- Source: https://www.fmz.com/strategy/427614 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-22 17:00:25). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Price ratios only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [9, 5, 15, 20]: **4 trials**; default 9 (the source's).

## Ambiguities resolved

- The average covers lags 1..n (the current bar is not in it), as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
