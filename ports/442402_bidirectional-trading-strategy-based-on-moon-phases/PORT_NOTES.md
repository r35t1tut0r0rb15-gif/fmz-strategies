# #442402 Bidirectional Trading Strategy Based on Moon Phases -> `fmz_442402_moon_age_phase_flip_reversal`

- FMZ source id: 442402 (lineage).
- Source: https://www.fmz.com/strategy/442402 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 16:15:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Calendar moon-age flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`flip_day` [15, 7]: **2 trials** (the age crossing that reads "new moon").

## Ambiguities resolved

- UTC calendar date; start date dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
