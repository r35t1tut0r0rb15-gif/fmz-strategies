# #440073 一个简单高效的MACD量化交易策略MACD-Crypto-Trading-Strategy -> `fmz_440073_sma_macd_hist_sign_state`

- FMZ source id: 440073 (lineage).
- Source: https://www.fmz.com/strategy/440073 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 14:20:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [12, 8] x `slow_length` [26, 50]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
