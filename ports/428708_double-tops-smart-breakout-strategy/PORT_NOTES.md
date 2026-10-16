# #428708 Double Tops Smart Breakout Strategy -> `fmz_428708_combo_123_pdo`

- FMZ source id: 428708 (lineage).
- Source: https://www.fmz.com/strategy/428708 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 15:17:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and close comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_ma` [200, 100]: **4 trials**; K smoothing 1, D 3, level 50, RSI 14 fixed.

## Ambiguities resolved

- Disagreement (0) closes all, as written; a direct long-to-short change reverses in one bar.
- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
