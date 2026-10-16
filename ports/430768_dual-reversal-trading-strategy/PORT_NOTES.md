# #430768 Dual Reversal Trading Strategy -> `fmz_430768_combo_123_n_bars_down`

- FMZ source id: 430768 (lineage).
- Source: https://www.fmz.com/strategy/430768 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 16:49:36). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430768. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `n_length` [4, 6]: **4 trials**; K smoothing 1, D 3, level 50 fixed.

## Ambiguities resolved

- The N-bars-down state never resets (short or flat only), as written. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
