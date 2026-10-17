# #484098 多指标趋势反转波动率条件选择性期权销售策略-Multi-Indicator-Trend-Reversal-Volatility-Conditional-Selective-Options-Selling-Strategy -> `fmz_484098_band_fade_low_adx_window`

- FMZ source id: 484098 (lineage).
- Source: https://www.fmz.com/strategy/484098 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:04:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-issue marked). |
| 2 | PASS | EMAs, bands, oscillators and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "Asia/Kolkata"] x `sl_atr` [2.0, 1.5]: **4 trials**; defaults UTC / 2 (the source as written);
target 3.5 ATR, EMA 50 / 200, DMI 14 (ADX <= 35), BB 20 x 1.8 and RSI 14 (65 / 35) fixed.

## Session open (check 9)

`timestamp(year, month, dayofmonth, 9, 20)` to `(15, 15)` in the chart's time zone, the bar's open time between them
(inclusive): UTC as written, or Asia/Kolkata (the NSE hours of the title) as the variant. Decision owed: which
reading to keep.

## Trailing stop (mark `trailing_stop_pending`)

The exits are re-issued every bar from the CURRENT close and ATR (a moving bracket). The port fixes them at the
signal bar.

## Ambiguities resolved

- The option legs are not modelled: "sell call" is a short and "sell put" a long, as the orders are. REVERSAL
  INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
