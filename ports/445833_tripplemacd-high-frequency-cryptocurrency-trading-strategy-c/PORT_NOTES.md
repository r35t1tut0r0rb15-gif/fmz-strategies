# #445833 TrippleMACD均线交叉与相对强弱指标结合的高频加密货币交易策略High-Frequency-Cryptocurrency-Trading-Strategy-Combining-TrippleMACD-Crossover-and-Relative-Strength-Index -> `fmz_445833_triple_macd_green_turn_linreg_rsi_tp_long`

- FMZ source id: 445833 (lineage).
- Source: https://www.fmz.com/strategy/445833 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 15:41:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed from the fill |
| 2 | PASS | MACD histogram colour change with linreg candle and RSI filters, fixed target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.04, 0.02] x `rsi_max` [55, 45]: **4 trials**; the MACD lengths and the linreg length fixed.

## Ambiguities resolved

- Fourth MACD repeats 34 / 144 as written; target 4 % of the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
