# #429488 Dual Indicator Slight Reversal Trading Strategy -> `fmz_429488_combo_123_ergodic_mdi`

- FMZ source id: 429488 (lineage).
- Source: https://www.fmz.com/strategy/429488 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 15:45:09). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a comparison of two series in the same units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [32, 16] x `u` [5, 10]: **4 trials**; s 5 and the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
