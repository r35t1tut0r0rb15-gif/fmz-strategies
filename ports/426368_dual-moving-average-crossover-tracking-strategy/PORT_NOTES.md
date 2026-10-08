# #426368 Dual Moving Average Crossover Tracking Strategy -> `fmz_426368_close_sma_cross_flatten`

- Source: https://www.fmz.com/strategy/426368 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 15:27:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A21). Not run.

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

`lma1` [10, 21, 50] x `lma2` [1, 3]: **6 trials**, defaults 21 / 1 (the source's; MA2 of length 1 is the close).

## Ambiguities resolved

- An opposite cross issues the reversing entry and close_all; filled in issue order they leave the bar flat (decision owed: sized-at-issue close_all would keep the reversal).
- lbars = 0 disables the lagged exits; date window dropped.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
