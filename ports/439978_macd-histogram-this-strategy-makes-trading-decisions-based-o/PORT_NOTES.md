# #439978 基于MACD指标的Histogram进行交易决策策略This-strategy-makes-trading-decisions-based-on-the-trend-of-MACD-Histogram -> `fmz_439978_sedkur_macd_histogram_trend_state`

- FMZ source id: 439978 (lineage).
- Source: https://www.fmz.com/strategy/439978 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 14:31:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram steps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hist_length` [1, 2] x `fast_length` [12, 8]: **4 trials**; slow 26, signal 9 fixed.

## Ambiguities resolved

- Flat histogram favours the short, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
