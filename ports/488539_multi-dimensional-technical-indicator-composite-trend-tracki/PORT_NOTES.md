# #488539 Multi Dimensional Technical Indicator Composite Trend Tracking Quantitative Trading Strategy -> `fmz_488539_golden_cross_rsi_vwap_supertrend_dir_atr_bracket_5m_reversal`

- FMZ source id: 488539 (lineage).
- Source: https://www.fmz.com/strategy/488539 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:22:09). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Golden / death crosses with RSI, VWAP and supertrend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.5] x `rr` [2.0, 1.5]: **4 trials**; EMA 50 / 200, RSI 14, supertrend 2 / 10.

## Ambiguities resolved

- Supertrend direction sign as written (+1 = down). Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
