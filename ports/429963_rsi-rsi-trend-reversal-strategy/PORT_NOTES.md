# #429963 RSI趋势反转策略RSI-Trend-Reversal-Strategy -> `fmz_429963_rsi_divergence_long`

- FMZ source id: 429963 (lineage).
- Source: https://www.fmz.com/strategy/429963 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 17:04:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after 5 bars. |
| 2 | PASS | RSI levels and price comparisons between pivots. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() fixed quantity 2 and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND366941. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [5, 14] x `lb` [5, 3] (left = right): **4 trials**; range 5-60 and the 75 exit fixed.

## Ambiguities resolved

- Strict pivot test (stated). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`none`
