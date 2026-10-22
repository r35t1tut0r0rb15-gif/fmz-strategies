# #442250 Reversal Momentum Strategy with Double Confirmation -> `fmz_442250_reversal123_donchian_width_combo`

- FMZ source id: 442250 (lineage).
- Source: https://www.fmz.com/strategy/442250 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 15:27:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and channel-width states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_dcw` [20, 40]: **4 trials**; smoothing 22 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
