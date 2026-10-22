# #454352 基于双均线交叉RSI和随机指标的短线量化交易策略-Short-term-Quantitative-Trading-Strategy-Based-on-Dual-Moving-Average-Crossover-RSI-and-Stochastic-Indicators -> `fmz_454352_sma20_50_cross_rsi_stoch_filter_reversal`

- FMZ source id: 454352 (lineage).
- Source: https://www.fmz.com/strategy/454352 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 15:35:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket pending (mark) |
| 2 | PASS | Filtered SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100] x `rsi_len` [7, 14]: **8 trials**; the stochastic and the levels fixed.

## Ambiguities resolved

- The moving bracket pending. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
