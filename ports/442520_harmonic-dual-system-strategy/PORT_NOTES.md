# #442520 Harmonic Dual System Strategy -> `fmz_442520_harmonic_mean_ladder_cross_reversal`

- FMZ source id: 442520 (lineage).
- Source: https://www.fmz.com/strategy/442520 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 15:49:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Harmonic-mean ladder crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders (the source has no input): **1 trial**, the source as written.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
