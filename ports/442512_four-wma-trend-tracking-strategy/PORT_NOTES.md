# #442512 Four WMA Trend Tracking Strategy -> `fmz_442512_four_wma_cross_pct_bracket`

- FMZ source id: 442512 (lineage).
- Source: https://www.fmz.com/strategy/442512 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 15:21:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | WMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.01, 0.02] x `sl_pct` [0.01, 0.02]: **4 trials**; the WMA lengths fixed.

## Ambiguities resolved

- Bracket as fixed fractions of the fill; a repeat signal's move not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
