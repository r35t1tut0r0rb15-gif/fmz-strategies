# #438458 Dynamic Trend Tracking Optimized Strategy -> `fmz_438458_ott_support_line_cross`

- FMZ source id: 438458 (lineage).
- Source: https://www.fmz.com/strategy/438458 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 11:20:04). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive support line and OTT crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital, commission and quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`percent` [0.1, 0.5] x `pds` [1, 2]: **4 trials**; CMO window 9 fixed; support-line condition.

## Ambiguities resolved

- Up / down terms take the price on the other bars as written; date window always true. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
