# #428968 Dual Oscillation Tracking Reversal Trading Strategy -> `fmz_428968_combo_123_chaikin_vol`

- FMZ source id: 428968 (lineage).
- Source: https://www.fmz.com/strategy/428968 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 14:47:25). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and the sign of a rate of change. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `roc_length` [12, 6]: **4 trials**; K smoothing 1, D 3, level 50, Chaikin EMA 10 and trigger 0 fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
