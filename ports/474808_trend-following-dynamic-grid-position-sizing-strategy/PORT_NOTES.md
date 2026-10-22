# #474808 Trend Following Dynamic Grid Position Sizing Strategy -> `fmz_474808_ttm_state_grid_1pct_levels_last_order_reversal`

- FMZ source id: 474808 (lineage).
- Source: https://www.fmz.com/strategy/474808 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 11:19:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TTM-state grid levels, one position at a time |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ttm_period` [6, 12] x `spacing` [0.01, 0.02]: **4 trials**; 5 levels.

## Ambiguities resolved

- Spacing used as a fraction (1 % steps), as written. The last order of a bar wins. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
