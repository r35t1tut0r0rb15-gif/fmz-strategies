# #440095 Moving Average Difference Zero Cross Strategy -> `fmz_440095_ema8_distance_turn_held_long`

- FMZ source id: 440095 (lineage).
- Source: https://www.fmz.com/strategy/440095 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 15:45:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA distance turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440095. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [8, 13]: **2 trials**.

## Ambiguities resolved

- Level-free exit places nothing; held to the end, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
