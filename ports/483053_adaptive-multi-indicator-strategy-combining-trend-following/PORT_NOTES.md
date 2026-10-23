# #483053 Adaptive Multi Indicator Strategy Combining Trend Following and Range Trading -> `fmz_483053_adx_regime_supertrend_vwap_bollinger_rsi_1h_reversal`

- FMZ source id: 483053 (lineage).
- Source: https://www.fmz.com/strategy/483053 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:08:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; position-price stop followed in the signals |
| 2 | PASS | Trend / range regime switch by ADX with supertrend, VWAP, Bollinger and RSI |
| 3 | PASS | Exchange pair in the header only (Nifty named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25.0, 20.0] x `st_mult` [2.0, 3.0]: **4 trials**; ATR 10, EMA 20 / 50, RSI 14, BB 20 x 2, stop 1 %.

## Ambiguities resolved

- Stop from position_avg_price at the signal, followed at the next open. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "regime_switch"`.

## Marks

`trailing_stop_pending`
