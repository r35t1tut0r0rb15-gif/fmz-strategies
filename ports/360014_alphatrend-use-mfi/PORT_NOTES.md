# #360014 AlphaTrend use mfi -> `fmz_360014_alphatrend_mfi14_atr5_line_cross_reversal`

- FMZ source id: 360014 (lineage).
- Source: https://www.fmz.com/strategy/360014 (PineScript, no @version line, author 发明者量化, FMZ last
  modified 2022-05-06 15:38:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MFI-switched ATR trailing line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coeff` [5.0, 1.0] x `ap` [14, 8]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
