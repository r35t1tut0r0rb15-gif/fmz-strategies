# #434682 Quantitative Trading Strategy Integrating Reversal and Future Lines of Demarcation -> `fmz_434682_combo_123_fld`

- FMZ source id: 434682 (lineage).
- Source: https://www.fmz.com/strategy/434682 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 12:00:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and a lagged-price comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 7] x `period` [40, 20]: **4 trials**; the 123 smoothing / D length / level fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
