# #489332 Dynamic EMA Crossover with RSI Trend Confirmation Quantitative Trading Strategy -> `fmz_489332_ema50_200_cross_rsi50_tick_bracket_reversal`

- FMZ source id: 489332 (lineage).
- Source: https://www.fmz.com/strategy/489332 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 15:05:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill |
| 2 | ADAPT | Tick bracket read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.0119, 0.5] x `tf_take_profit_ratio` [2.0, 3.0]: **4 trials**; EMA 50 / 200, RSI 14.

## Ambiguities resolved

- Ticks read at BTC 42000; the short's mirrored-wrong levels close it at once, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
