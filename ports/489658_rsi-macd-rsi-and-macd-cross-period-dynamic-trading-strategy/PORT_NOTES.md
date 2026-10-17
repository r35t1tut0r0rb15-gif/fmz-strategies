# #489658 RSI与MACD交叉多周期动态交易策略-RSI-and-MACD-Cross-Period-Dynamic-Trading-Strategy -> `fmz_489658_macd_cross_rsi_extreme_bracket`

- FMZ source id: 489658 (lineage).
- Source: https://www.fmz.com/strategy/489658 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 13:50:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Oscillators and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_oversold` [30, 40] x `sl_pct` [2.0, 1.0]: **4 trials**; defaults 30 / 2 (the source's); RSI 14, overbought 70,
MACD 12 / 26 / 9 and the 5 % target fixed.

## Ambiguities resolved

- The bracket is placed on the signal bar; re-based on the fill (house rule).
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
