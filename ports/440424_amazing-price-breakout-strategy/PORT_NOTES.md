# #440424 Amazing Price Breakout Strategy -> `fmz_440424_engulfing_sma15_rsi_atr_stop`

- FMZ source id: 440424 (lineage).
- Source: https://www.fmz.com/strategy/440424 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 15:07:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Engulfing candles, SMA and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [0.75, 2.0] x `ma_len` [15, 30]: **4 trials**; ATR and RSI 14 fixed.

## Ambiguities resolved

- Stop from the signal close; later moves not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
