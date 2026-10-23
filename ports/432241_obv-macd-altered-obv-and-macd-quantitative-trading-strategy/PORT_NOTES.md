# #432241 基于改动OBV和MACD的量化交易策略Altered-OBV-and-MACD-Quantitative-Trading-Strategy -> `fmz_432241_altered_obv_macd_cross_price_macd_filter_reversal`

- FMZ source id: 432241 (lineage).
- Source: https://www.fmz.com/strategy/432241 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 17:58:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD of an on-balance volume variant |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): margin_long 100, margin_short 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [12, 8] x `slow_len` [26, 34]: **4 trials**; signal 9, price MACD 12 / 26 / 9.

## Ambiguities resolved

- rising / falling as earlier ports. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`none`
