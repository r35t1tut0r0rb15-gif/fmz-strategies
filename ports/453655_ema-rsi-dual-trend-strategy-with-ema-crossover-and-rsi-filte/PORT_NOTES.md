# #453655 EMA交叉与RSI过滤的双重趋势策略-Dual-Trend-Strategy-with-EMA-Crossover-and-RSI-Filter -> `fmz_453655_ema9_21_cross_rsi_macd_confirm_reversal`

- FMZ source id: 453655 (lineage).
- Source: https://www.fmz.com/strategy/453655 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:29:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Confirmed EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50] x `rsi_len` [14, 7]: **8 trials**; the MACD lengths and RSI levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
