# #434484 Double Reversal Percentage Change Bar Quantitative Strategy -> `fmz_434484_combo_123_percent_change`

- FMZ source id: 434484 (lineage).
- Source: https://www.fmz.com/strategy/434484 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 17:44:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and percent changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `zone` [0.33, 0.66]: **4 trials**; the 123 smoothing / D length / level and look back 1 fixed.

## Ambiguities resolved

- Symmetric zones from one grid value. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
