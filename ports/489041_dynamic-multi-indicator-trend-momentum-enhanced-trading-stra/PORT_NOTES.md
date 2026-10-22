# #489041 Dynamic Multi Indicator Trend Momentum Enhanced Trading Strategy -> `fmz_489041_ema20_50_cross_ema200_rsi55_macd_atr_bracket_long`

- FMZ source id: 489041 (lineage).
- Source: https://www.fmz.com/strategy/489041 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 14:41:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with trend / RSI / MACD filters and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 2.5] x `risk_reward_ratio` [2.0, 3.0]: **4 trials**; EMA 20 / 50 / 200, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- Same-side re-sends are pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
