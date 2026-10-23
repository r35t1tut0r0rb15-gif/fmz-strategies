# #377541 AlphaTrend Strategy -> `fmz_377541_alphatrend_mfi14_atr1_line_lag2_cross_reversal`

- FMZ source id: 377541 (lineage).
- Source: https://www.fmz.com/strategy/377541 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-08-12 16:51:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MFI-switched ATR trailing line against its own lag |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 % long / short stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG377541. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coeff` [1.0, 2.0] x `ap` [14, 8]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
