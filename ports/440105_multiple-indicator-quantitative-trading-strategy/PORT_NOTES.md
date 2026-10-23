# #440105 Multiple Indicator Quantitative Trading Strategy -> `fmz_440105_eight_condition_agreement_edge_pct_bracket_1h_reversal`

- FMZ source id: 440105 (lineage).
- Source: https://www.fmz.com/strategy/440105 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 16:19:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal close as fractions of the fill |
| 2 | PASS | Eight-condition trend agreement edges |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = qn (1 with averaging on), not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop` [0.005, 0.01] x `profit` [0.015, 0.03]: **4 trials**; all indicator settings fixed.

## Ambiguities resolved

- Bracket fixed at the opening signal's close; 1e-6 floor. Volume = broker tick volume (VWAP, VWMA, volume EMA). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
