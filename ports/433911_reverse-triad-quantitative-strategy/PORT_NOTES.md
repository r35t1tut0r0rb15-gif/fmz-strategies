# #433911 Reverse Triad Quantitative Strategy -> `fmz_433911_combo_123_accelerator`

- FMZ source id: 433911 (lineage).
- Source: https://www.fmz.com/strategy/433911 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 14:14:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and an average-difference sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430763. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `slow` [34, 55]: **4 trials**; the 123 smoothing / level and AC fast 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
