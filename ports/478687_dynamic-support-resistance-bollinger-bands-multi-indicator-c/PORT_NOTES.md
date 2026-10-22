# #478687 Dynamic Support Resistance Bollinger Bands Multi Indicator Cross Strategy -> `fmz_478687_pivot_sr_zone_cross_bb20_extreme_long`

- FMZ source id: 478687 (lineage).
- Source: https://www.fmz.com/strategy/478687 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:24:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot-zone crossings at the Bollinger extremes |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd` [10, 5] x `channel_w` [10, 5]: **4 trials**; max 20 pivots, 5 zones, strength 2, BB 20 / 2.

## Ambiguities resolved

- No bar size in the source (bar_size_pending). The zone mid is not tick-rounded. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`bar_size_pending`
