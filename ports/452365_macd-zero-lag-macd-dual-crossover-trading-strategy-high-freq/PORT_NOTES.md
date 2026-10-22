# #452365 MACD双转换零滞后交易策略-基于短期趋势捕捉的高频交易-Zero-Lag-MACD-Dual-Crossover-Trading-Strategy-High-Frequency-Trading-Based-on-Short-Term-Trend-Capture -> `fmz_452365_zero_lag_macd_cross_beyond_zero_reversal`

- FMZ source id: 452365 (lineage).
- Source: https://www.fmz.com/strategy/452365 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-05-24 18:14:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zero-lag MACD crossings on the far side of zero |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21] x `signal_len` [9, 5]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
