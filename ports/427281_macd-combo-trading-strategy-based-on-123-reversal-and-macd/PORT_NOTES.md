# #427281 Combo Trading Strategy Based on 123 Reversal and MACD -> `fmz_427281_combo_123_ergodic_macd`

- FMZ source id: 427281 (lineage).
- Source: https://www.fmz.com/strategy/427281 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 17:17:30). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `level` [50, 40] x `r` [14, 9]: **8 trials**; defaults 14 / 50 / 14 (the source's); K 1, D 3, MACD slow 21, signal 5 fixed.

## Ambiguities resolved

- Each sub-signal keeps its last state (nz(pos[1])); the combo is flat when they disagree (close_all).
- fADX is never used. REVERSAL INTENDED. FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
