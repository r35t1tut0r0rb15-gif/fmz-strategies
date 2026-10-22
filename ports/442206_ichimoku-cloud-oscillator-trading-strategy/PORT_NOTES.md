# #442206 Ichimoku Cloud Oscillator Trading Strategy -> `fmz_442206_close_ichimoku_span_b_cross_reversal`

- FMZ source id: 442206 (lineage).
- Source: https://www.fmz.com/strategy/442206 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 11:12:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / span B crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`span_b` [52, 26]: **2 trials**.

## Ambiguities resolved

- Undisplaced span B. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
