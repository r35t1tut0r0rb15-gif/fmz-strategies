# #483029 Multi Indicator Trend Following Momentum Trading Strategy -> `fmz_483029_macd_cross_sma200_rsi50_ema50_pullback_rr_bracket_reversal`

- FMZ source id: 483029 (lineage).
- Source: https://www.fmz.com/strategy/483029 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:06:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | MACD crossings with SMA / RSI / pullback filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_reward` [1.5, 1.0] x `pullback_bars` [5, 10]: **4 trials**; SMA 200, EMA 50, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- As written (intended version owed): RR used as a price fraction; the short target is unreachable. trail_price alone is no trail.
- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
