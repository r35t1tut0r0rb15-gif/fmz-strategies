# #484098 Multi Indicator Trend Reversal Volatility Conditional Selective Options Selling Strategy -> `fmz_484098_bb_rsi_extreme_fade_against_ema_trend_adx_atr_utc_window_reversal`

- FMZ source id: 484098 (lineage).
- Source: https://www.fmz.com/strategy/484098 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:04:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close bracket pending |
| 2 | PASS | Bollinger / RSI extremes against the EMA trend with ADX / ATR filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [1.8, 2.5] x `rsi_length` [14, 7]: **4 trials**; EMA 50 / 200, ADX 14 under 35, ATR 14, window 09:20-15:15 UTC.

## Ambiguities resolved

- The window is read in UTC. The per-bar bracket is pending, not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
