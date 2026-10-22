# #451492 布林带ATR趋势跟踪策略-Bollinger-Band-ATR-Trend-Following-Strategy -> `fmz_451492_bollinger_cross_close_atr_trail_reversal`

- FMZ source id: 451492 (lineage).
- Source: https://www.fmz.com/strategy/451492 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 10:50:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band crossings with a trailing-line trigger |
| 3 | PASS | Exchange pair in the header only (the 'AAPL' variable is unused). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `mult` [2.0, 2.5] x `atr_len` [10, 20]: **8 trials**; the key value 1 fixed.

## Ambiguities resolved

- Call order on shared ids. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger"`.

## Marks

`none`
