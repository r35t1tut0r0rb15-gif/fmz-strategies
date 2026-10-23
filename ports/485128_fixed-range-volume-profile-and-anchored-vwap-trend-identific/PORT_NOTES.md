# #485128 Fixed Range Volume Profile And Anchored VWAP Trend Identification Strategy With Dynamic Stop Loss -> `fmz_485128_session_vwap_cross_ema200_rsi_macd_volume_atr_stop_1h_reversal`

- FMZ source id: 485128 (lineage).
- Source: https://www.fmz.com/strategy/485128 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 11:14:10). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal close as a fraction of the fill |
| 2 | PASS | Session-VWAP crossings in the EMA 200 trend with RSI / MACD / volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.5] x `ema_len` [200, 100]: **4 trials**; RSI 14, MACD 12 / 26 / 9, volume SMA 20.

## Ambiguities resolved

- No trailing stop (no offset). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
