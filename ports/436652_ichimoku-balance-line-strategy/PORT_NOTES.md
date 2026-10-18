# #436652 Ichimoku Balance Line Strategy -> `fmz_436652_ichimoku_cloud_breakout`

- FMZ source id: 436652 (lineage).
- Source: https://www.fmz.com/strategy/436652 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-26 16:13:42). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C94). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud breakout |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429159. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [18, 9] x `span_offset` [52, 26]: **4 trials**; Kijun 60 and Senkou B 30 fixed.

## Ambiguities resolved

- Only the cloud breakouts trade. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
