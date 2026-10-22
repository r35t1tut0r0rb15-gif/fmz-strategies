# #482670 基于多均线趋势和ATR动态止盈止损的加密货币交易策略-Multi-EMA-Trend-Following-with-Dynamic-ATR-Based-Exit-Strategy-for-Cryptocurrency-Trading -> `fmz_482670_ema9_20_cross_ema50_dist_rsi_daily_one_atr_bracket_reversal`

- FMZ source id: 482670 (lineage).
- Source: https://www.fmz.com/strategy/482670 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:45:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket from the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with trend-distance and RSI filters, one per day |
| 3 | PASS | No exchange header. |
| 4 | DONE | 2 % of equity and the equity-risk quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_distance_atr` [1.1, 0.5] x `rsi_buy_low` [45, 50]: **4 trials**; EMA 9 / 20 / 50, ATR 14, SL / TP by ticker.

## Ambiguities resolved

- The slope filters compare a price level with +/- 0.2, as written (shorts only under 0.2).
- The ticker multiples are chosen from the symbol key. A repeat signal's re-sent bracket is pending.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
