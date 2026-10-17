# #434165 123反转与STARC波段组合策略123-Reversal-and-STARC-Bands-Combo-Strategy -> `fmz_434165_combo_123_starc`

- FMZ source id: 434165 (lineage).
- Source: https://www.fmz.com/strategy/434165 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-04 13:38:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `k` [1.33, 2.0]: **4 trials**; the 123 smoothing / level, STARC MA 5 and ATR 15 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
