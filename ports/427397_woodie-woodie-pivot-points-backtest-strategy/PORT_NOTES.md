# #427397 Woodie Pivot Points Backtest Strategy -> `fmz_427397_woodie_pivot`

- FMZ source id: 427397 (lineage).
- Source: https://www.fmz.com/strategy/427397 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 17:08:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous completed day. |
| 2 | PASS | Comparisons with the instrument's own pivot. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`close_weight` [2, 1]: **2 trials**; default 2 (Woodie's pivot as written; 1 = the classic (H + L + C) / 3). The source has no numeric input besides an unused width.

## Ambiguities resolved

- `security('D', x[1])` on the daily chart = the previous broker day's value.
- REVERSAL INTENDED. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
