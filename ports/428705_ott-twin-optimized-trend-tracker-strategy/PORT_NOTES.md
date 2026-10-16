# #428705 双OTT趋势跟踪策略Twin-Optimized-Trend-Tracker-Strategy -> `fmz_428705_twin_ott_var`

- FMZ source id: 428705 (lineage).
- Source: https://www.fmz.com/strategy/428705 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 15:10:31). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Percentages of the moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND361567. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [40, 20] x `percent` [1.0, 2.0]: **4 trials**; twin coefficient 0.001, CMO 9 and source close fixed.

## Ambiguities resolved

- VAR only (the default type). Lines read two bars back, as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
