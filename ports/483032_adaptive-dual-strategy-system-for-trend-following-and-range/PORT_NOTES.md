# #483032 Adaptive Dual Strategy System for Trend Following and Range Trading -> `fmz_483032_adx25_trend_sma_cross_range_bb_reentry_atr_bracket_reversal`

- FMZ source id: 483032 (lineage).
- Source: https://www.fmz.com/strategy/483032 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:17:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | ADX regime switch between SMA crossings and band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_mult` [1.5, 2.0] x `take_profit_mult` [3.0, 2.0]: **4 trials**; ADX 14 / 25, SMA 50 / 200, Bollinger 20 / 2, RSI 14, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
