# #442211 CDC动作区域策略CDC-Action-Zone-Strategy -> `fmz_442211_cdc_action_zone_colour_reversal`

- FMZ source id: 442211 (lineage).
- Source: https://www.fmz.com/strategy/442211 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 11:23:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Action Zone colour changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429787. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd1` [12, 8] x `prd2` [26, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
