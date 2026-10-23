# #361480 AlphaTrend -> `fmz_361480_alphatrend_mfi8_atr1_two_bar_turn_alternating_reversal`

- FMZ source id: 361480 (lineage).
- Source: https://www.fmz.com/strategy/361480 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-06 15:49:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MFI-switched ATR trailing line turns, alternating |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coeff` [1.0, 2.0] x `ap` [8, 14]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
