# #427574 Hawk Eye Short term Trading Strategy -> `fmz_427574_ema21_55_macd_rise_vwma55_144_stoch_rsi_reversal`

- FMZ source id: 427574 (lineage).
- Source: https://www.fmz.com/strategy/427574 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-22 12:09:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD momentum with VWMA order and stochastic filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [21, 12] x `slow_length` [55, 26]: **4 trials**; stoch 8 / 5, stoch RSI 8 / 21 / 5, VWMA 55 / 144.

## Ambiguities resolved

- Header 1d over the title's 1H. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
