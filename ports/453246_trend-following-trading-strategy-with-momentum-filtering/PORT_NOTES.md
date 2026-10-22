# #453246 Trend Following Trading Strategy with Momentum Filtering -> `fmz_453246_macd_cross_rsi50_filter_reversal`

- FMZ source id: 453246 (lineage).
- Source: https://www.fmz.com/strategy/453246 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 11:23:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stops pending (mark) |
| 2 | PASS | MACD crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21] x `rsi_len` [14, 7]: **8 trials**; the signal 9 and the RSI 50 fixed.

## Ambiguities resolved

- Moving stops pending (not ported). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
