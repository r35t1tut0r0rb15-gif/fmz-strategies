# #435165 Concise Dynamic Trend Strategy -> `fmz_435165_traders_dynamic_index_alerts`

- FMZ source id: 435165 (lineage).
- Source: https://www.fmz.com/strategy/435165 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 18:03:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI bands and a smoothed price channel |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`strength` [2, 1] x `lenh` [5, 10]: **4 trials**; the TDI lengths and levels fixed.

## Ambiguities resolved

- First alert of a sequence enters; disabled TP / SL not ported. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
