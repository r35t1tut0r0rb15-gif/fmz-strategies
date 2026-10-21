# #438463 Bear Power Tracking Strategy -> `fmz_438463_elder_bear_power_state`

- FMZ source id: 438463 (lineage).
- Source: https://www.fmz.com/strategy/438463 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-12 11:43:08). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Low against an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430065. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [13, 26, 8, 50]: **4 trials**; trigger 0 and reverse off.

## Ambiguities resolved

- DayLow = the bar's low on daily bars. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
