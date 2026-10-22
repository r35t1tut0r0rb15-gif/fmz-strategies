# #442275 Quantitative Trading Strategy Based on Ichimoku Cloud and Moving Average -> `fmz_442275_ema50_side_cloud_colour_reversal`

- FMZ source id: 442275 (lineage).
- Source: https://www.fmz.com/strategy/442275 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 17:12:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side and cloud colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [50, 100] x `base` [26, 52]: **4 trials**; conversion 9 and span B 52 fixed.

## Ambiguities resolved

- The short close never fires (opentrades < 0), as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
