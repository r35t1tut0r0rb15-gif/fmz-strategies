# #426888 Quantitative Trading Strategy with Multi Indicator Confirmation -> `fmz_426888_combo_123_reversal_williams_ad`

- Source: https://www.fmz.com/strategy/426888 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 11:55:04). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426888` (Jaccard 0.65-0.80) with #427813 (PORT_CANDIDATE), #427883 (PORT_CANDIDATE), #428582 (PORT_CANDIDATE), #428626 (PORT_CANDIDATE), #428855 (PORT_CANDIDATE), #429485 (PORT_CANDIDATE), #429771 (PORT_CANDIDATE), #430269 (PORT_CANDIDATE), #430555 (PORT_CANDIDATE), #431408 (PORT_CANDIDATE), #432231 (PORT_CANDIDATE), #432883 (PORT_CANDIDATE), #432921 (PORT_CANDIDATE), #433138 (PORT_CANDIDATE), #434484 (PORT_CANDIDATE), #435288 (PORT_CANDIDATE), #435291 (PORT_CANDIDATE), #435701 (PORT_CANDIDATE), #435837 (PORT_CANDIDATE), #436094 (PORT_CANDIDATE), #436215 (PORT_CANDIDATE), #436770 (PORT_CANDIDATE), #437515 (PORT_CANDIDATE), #437658 (PORT_CANDIDATE), #438457 (PORT_CANDIDATE), #439087 (PORT_CANDIDATE), #440094 (PORT_CANDIDATE), #440369 (PORT_CANDIDATE), #441961 (PORT_CANDIDATE), #442823 (PORT_CANDIDATE); best Jaccard 0.659 with #440094. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `length_wad` [14, 28]: **4 trials**, defaults 14 / 14 (the source's); k 1, d 3, level 50 fixed.

## Ambiguities resolved

- As written an unchanged close resets the A/D sum to 0; the sum starts from nz 0.
- "Trade reverse" off.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
