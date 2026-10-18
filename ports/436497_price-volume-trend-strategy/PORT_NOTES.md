# #436497 Price Volume Trend Strategy -> `fmz_436497_ha_state_strength_eliminator`

- FMZ source id: 436497 (lineage).
- Source: https://www.fmz.com/strategy/436497 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 13:09:48). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Heikin-Ashi state and a price-unit strength threshold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [600, 300] x `len` [1, 2]: **4 trials**; strength scale 10000 fixed.

## Ambiguities resolved

- Price-unit threshold as written; first signal cannot trade; doji exclusion only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
