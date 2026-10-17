# #432213 基于均线和MACD指标的量化交易策略Trend-Following-Strategy-Based-on-Moving-Average-and-MACD -> `fmz_432213_zlsma_macd_cross`

- FMZ source id: 432213 (lineage).
- Source: https://www.fmz.com/strategy/432213 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 15:58:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression-line turns and a MACD cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [32, 16] x `slow` [400, 200]: **4 trials**; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Both entries need macd >= signal, as written. A close after the entries leaves a same-side bar flat. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
