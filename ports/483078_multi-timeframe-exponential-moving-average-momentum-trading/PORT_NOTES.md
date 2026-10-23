# #483078 Multi Timeframe Exponential Moving Average Momentum Trading Strategy with Volume Weighted Average Price and RSI Confirmation -> `fmz_483078_ema9_21_cross_session_vwap_rsi_atr_rr2_1h_reversal`

- FMZ source id: 483078 (lineage).
- Source: https://www.fmz.com/strategy/483078 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:50:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA crossings on the session-VWAP side with an RSI filter |
| 3 | PASS | Exchange pair in the header only (BTC named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.0] x `rr` [2.0, 1.5]: **4 trials**; EMA 9 / 21, RSI 14, ATR 14.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
