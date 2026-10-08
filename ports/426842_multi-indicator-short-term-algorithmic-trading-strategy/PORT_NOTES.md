# #426842 Multi Indicator Short Term Algorithmic Trading Strategy -> `fmz_426842_hull_ichimoku_macd_dayfilter`

- Source: https://www.fmz.com/strategy/426842 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 19:46:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426842` (Jaccard >= 0.80) with #437555 (DUPLICATE), #437763 (REJECTED); best Jaccard 0.840 with #437555. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [14, 21] x `dt` [0.001, 0.005]: **4 trials**, defaults 14 / 0.001 (the source's); Ichimoku 9 / 26 / 52 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Daily close change on broker days from the 4h bars; lookahead_off shows the last completed day (the new day's value from the bar whose end reaches 17:00 New York).
- openprofit thresholds in account currency are balance checks: sizing.
- Closes come before entries; a closing bar opens nothing.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
