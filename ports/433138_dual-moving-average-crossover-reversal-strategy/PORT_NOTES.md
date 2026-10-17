# #433138 Dual Moving Average Crossover Reversal Strategy -> `fmz_433138_combo_123_dinapoli`

- FMZ source id: 433138 (lineage).
- Source: https://www.fmz.com/strategy/433138 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 17:03:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and the close against its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `din_len` [14, 28]: **4 trials**; the 123 smoothing / level and trigger 0 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
