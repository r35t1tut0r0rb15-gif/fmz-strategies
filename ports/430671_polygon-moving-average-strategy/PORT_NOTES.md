# #430671 Polygon Moving Average Strategy -> `fmz_430671_ema_stack_pct_trail`

- FMZ source id: 430671 (lineage).
- Source: https://www.fmz.com/strategy/430671 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 14:53:50). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated). |
| 2 | PASS | Moving averages and percentage trail distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.02, 0.04] x `activate` [0.05, 0.02]: **4 trials**; EMA 3 / 7 / 13 fixed.

## Ambiguities resolved

- House percent trail from the fill (the source re-sizes from each close). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop`
