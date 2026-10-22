# #482891 使用RSI和MACD双重过滤的动态止损趋势跟踪策略-Dynamic-Stop-Loss-Trend-Following-Strategy-with-RSI-and-MACD-Dual-Filtering -> `fmz_482891_macd_cross_rsi14_40_59_close_stop3pct_reversal`

- FMZ source id: 482891 (lineage).
- Source: https://www.fmz.com/strategy/482891 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:50:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based percent stop |
| 2 | PASS | MACD crossings with RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percent` [3.0, 1.5] x `rsi_length` [14, 7]: **4 trials**; RSI levels 59 / 40, MACD 12 / 26 / 9.

## Ambiguities resolved

- A repeat same-side signal resets the stop's reference close, as written. MPL 2.0 source, ported and stated.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
