# #432784 Bitcoin Trading Strategy Based on Chinese Zodiac Calendar -> `fmz_432784_zodiac_year_cycle`

- FMZ source id: 432784 (lineage).
- Source: https://www.fmz.com/strategy/432784 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 14:50:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A calendar rule |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`year_offset` [0]: **1 trial** (the rule as written; no parameter to vary).

## Ambiguities resolved

- Broker-day year; one-bar New Year difference stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
