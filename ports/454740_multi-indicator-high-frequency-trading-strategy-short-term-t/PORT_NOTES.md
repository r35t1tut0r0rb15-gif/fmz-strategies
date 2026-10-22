# #454740 Multi Indicator High Frequency Trading Strategy Short Term Trading System Combining Exponential Moving Averages and Momentum Indicators -> `fmz_454740_ema5_10_cross_rsi_filter_reversal`

- FMZ source id: 454740 (lineage).
- Source: https://www.fmz.com/strategy/454740 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 15:23:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [10, 21] x `rsi_len` [14, 7]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
