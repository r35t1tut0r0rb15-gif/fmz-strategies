# #488137 Multi Indicator Comprehensive Analysis Quantitative Trading Strategy Trend Momentum and Volatility Collaborative Prediction Model -> `fmz_488137_many_indicator_golden_cross_volume_atr_bracket_3m_reversal`

- FMZ source id: 488137 (lineage).
- Source: https://www.fmz.com/strategy/488137 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 13:50:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Many-indicator agreement on golden / death crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [2.0, 1.5] x `tp_atr` [4.0, 3.0]: **4 trials**; SL 2 ATR, the indicator lengths as written.

## Ambiguities resolved

- Exits without from_entry read per trade. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`none`
