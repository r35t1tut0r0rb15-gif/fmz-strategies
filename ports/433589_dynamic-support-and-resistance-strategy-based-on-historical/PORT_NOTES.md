# #433589 Dynamic Support and Resistance Strategy Based on Historical Data -> `fmz_433589_daily_pivot_break`

- FMZ source id: 433589 (lineage).
- Source: https://www.fmz.com/strategy/433589 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-28 17:04:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | The close against daily pivot levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` ["1", "2"]: **2 trials** (R1 / S1 as written, or R2 / S2).

## Ambiguities resolved

- Daily pivots from completed broker days; breakout reading as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
