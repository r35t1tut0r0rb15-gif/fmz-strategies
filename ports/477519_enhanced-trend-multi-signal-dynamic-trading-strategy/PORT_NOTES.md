# #477519 Enhanced Trend Multi Signal Dynamic Trading Strategy -> `fmz_477519_supertrend10x3_contrarian_direction_reversal`

- FMZ source id: 477519 (lineage).
- Source: https://www.fmz.com/strategy/477519 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:06:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Contrarian SuperTrend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 20]: **4 trials**.

## Ambiguities resolved

- Trades against the SuperTrend direction, as written; the custom signals never change the position. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
