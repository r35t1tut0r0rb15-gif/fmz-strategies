# #429383 Dual Moving Average Reversal Trading Strategy -> `fmz_429383_daily_close_sma_window`

- FMZ source id: 429383 (lineage).
- Source: https://www.fmz.com/strategy/429383 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 15:50:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days. |
| 2 | PASS | Price vs a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the off-by-default TP / SL stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429383. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28]: **2 trials**; the daily series and the UTC window fixed.

## Ambiguities resolved

- Daily close = last completed broker day. Exchange time taken as UTC. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
