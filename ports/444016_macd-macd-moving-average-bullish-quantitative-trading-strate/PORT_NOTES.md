# #444016 MACD均线多头量化交易策略MACD-Moving-Average-Bullish-Quantitative-Trading-Strategy -> `fmz_444016_macd_cross_above_zero_sma20_long`

- FMZ source id: 444016 (lineage).
- Source: https://www.fmz.com/strategy/444016 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:47:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings above zero with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [20, 50] x `macd_fast` [12, 8]: **4 trials**; the slow and signal lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
