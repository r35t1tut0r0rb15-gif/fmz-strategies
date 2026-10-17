# #432970 Cloud Soaring High Yield Daily Trading Strategy -> `fmz_432970_ichimoku_cross_above_cloud`

- FMZ source id: 432970 (lineage).
- Source: https://www.fmz.com/strategy/432970 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 10:56:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku line crosses and cloud position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `kijun` [26, 60]: **4 trials**; span B 52 and displacement 26 fixed.

## Ambiguities resolved

- Spans read 26 bars back as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
