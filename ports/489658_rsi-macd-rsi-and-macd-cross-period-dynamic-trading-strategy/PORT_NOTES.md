# #489658 RSI与MACD交叉多周期动态交易策略-RSI-and-MACD-Cross-Period-Dynamic-Trading-Strategy -> `fmz_489658_macd_cross_rsi_extreme_pct_bracket_reversal`

- FMZ source id: 489658 (lineage).
- Source: https://www.fmz.com/strategy/489658 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 13:50:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | MACD crossings at RSI extremes with a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`takeProfitPerc` [5.0, 2.0] x `stopLossPerc` [2.0, 1.0]: **4 trials**; RSI 14 / 30 / 70, MACD 12 / 26 / 9.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "15min". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
