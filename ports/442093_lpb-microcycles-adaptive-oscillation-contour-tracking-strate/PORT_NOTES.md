# #442093 LPB Microcycles Adaptive Oscillation Contour Tracking Strategy -> `fmz_442093_hp_filter_cross_over_price_swing_atr_bracket_1h_long_only`

- FMZ source id: 442093 (lineage).
- Source: https://www.fmz.com/strategy/442093 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 11:32:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal bar as fractions of the fill |
| 2 | PASS | Hodrick-Prescott filter crossing over price with a swing / ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lam` [1000.0, 100.0] x `rr` [1.0, 2.0]: **4 trials**; filter length 100, stop ATR 14 x 1.

## Ambiguities resolved

- HP end-point weights from the script's own solve; the VWAP equals HP. Volume not used. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "regression_bands"`.

## Marks

`none`
