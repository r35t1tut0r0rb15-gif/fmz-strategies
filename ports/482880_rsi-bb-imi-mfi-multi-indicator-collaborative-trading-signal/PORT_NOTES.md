# #482880 RSI BB IMI MFI Multi Indicator Collaborative Trading Signal Generation Strategy RSI BB IMI MFI -> `fmz_482880_rsi_bb_imi_mfi_extreme_agreement_1h_reversal`

- FMZ source id: 482880 (lineage).
- Source: https://www.fmz.com/strategy/482880 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:23:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Four-oscillator oversold / overbought agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_lo` [30.0, 35.0] x `mfi_lo` [20.0, 30.0]: **4 trials**; BB 20 x 2, IMI 14, MFI 14.

## Ambiguities resolved

- The sell compares with the BB basis (destructuring order). Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_agreement"`.

## Marks

`none`
