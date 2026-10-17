# #432423 Multiple Trend Tracking Strategy -> `fmz_432423_macd_rsi_cross_flip`

- FMZ source id: 432423 (lineage).
- Source: https://www.fmz.com/strategy/432423 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-17 17:19:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram and RSI crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [18, 14] x `fast` [12, 8]: **4 trials**; slow 26, signal 9 and the RSI levels fixed.

## Ambiguities resolved

- The later statement wins a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
