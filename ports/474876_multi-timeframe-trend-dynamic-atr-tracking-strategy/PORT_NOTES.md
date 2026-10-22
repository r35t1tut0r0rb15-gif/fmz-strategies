# #474876 Multi Timeframe Trend Dynamic ATR Tracking Strategy -> `fmz_474876_ema9_21_cross_rsi_ema21_macd_filters_reversal`

- FMZ source id: 474876 (lineage).
- Source: https://www.fmz.com/strategy/474876 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 16:24:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with RSI / EMA / MACD filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50]: **4 trials**; RSI / MACD fixed.

## Ambiguities resolved

- The when=-armed ATR exits never act (the opposite entry reverses first). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
