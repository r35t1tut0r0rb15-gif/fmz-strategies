# #442924 Short term Trading Strategy Based on Momentum Indicator -> `fmz_442924_hpotter_mass_index_trigger_reversal`

- FMZ source id: 442924 (lineage).
- Source: https://www.fmz.com/strategy/442924 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-27 14:07:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Mass Index against a trigger |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length2` [25, 50] x `trigger` [26.5, 27.0]: **4 trials** (the trigger scales with the sum length as written); the EMA length fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
