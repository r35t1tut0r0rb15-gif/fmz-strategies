# #427985 Dual Trend Tracking Strategy -> `fmz_427985_combo_123_reversal_obos`

- FMZ source id: 427985 (lineage).
- Source: https://www.fmz.com/strategy/427985 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:14:25). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `length_oo` [10, 20]: **4 trials**; defaults 14 / 10 (the source's); K 1, D 3, level 50, bands 0.92 / 0.5 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off. Disagreement closes the position. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
