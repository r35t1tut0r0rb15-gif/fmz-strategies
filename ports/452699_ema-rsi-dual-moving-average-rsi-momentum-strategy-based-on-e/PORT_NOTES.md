# #452699 基于EMA与趋势线突破的双均线-RSI-动量策略-Dual-Moving-Average-RSI-Momentum-Strategy-Based-on-EMA-and-Trendline-Breakouts -> `fmz_452699_sma10_30_cross_rsi_filter_reversal`

- FMZ source id: 452699 (lineage).
- Source: https://www.fmz.com/strategy/452699 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 11:28:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an RSI filter |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [30, 50] x `rsi_len` [14, 7]: **8 trials**; the breakout lookback 50 and the RSI levels fixed.

## Ambiguities resolved

- The breakout alternatives never fire (current bar included). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
