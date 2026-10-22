# #453653 MACD与RSI相结合的多重过滤日内交易策略-MACD-and-RSI-Multi-Filter-Intraday-Trading-Strategy -> `fmz_453653_macd_cross_sma50_200_rsi_filter_reversal`

- FMZ source id: 453653 (lineage).
- Source: https://www.fmz.com/strategy/453653 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:20:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Filtered MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `rsi_len` [14, 7] x `trend_slow` [200, 100]: **8 trials**; the SMA 50 and RSI levels fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
