# #483511 Multi Indicator Trend Momentum Trading Strategy with Dynamic Risk Management System -> `fmz_483511_ema20_50_cross_rsi_macd_volume_atr_stop_1h_reversal`

- FMZ source id: 483511 (lineage).
- Source: https://www.fmz.com/strategy/483511 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 09:50:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal close as a fraction of the fill |
| 2 | PASS | EMA crossings confirmed by RSI, MACD and volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty and 5 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_mult` [3.5, 2.5] x `vol_mult` [2.0, 1.5]: **4 trials**; EMA 20 / 50, RSI 14, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- Fixed stop from the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
