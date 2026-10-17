# #486564 双均线交叉量化交易策略基于短期与中期移动平均线突破系统-Dual-Moving-Average-Crossover-Trading-System-A-Quantitative-Strategy-Based-on-Short-term-and-Medium-term-MA-Breakthrough -> `fmz_486564_sma7_10_cross_long_only`

- FMZ source id: 486564 (lineage).
- Source: https://www.fmz.com/strategy/486564 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:27:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair (TRUMP_USDT) in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 5] x `slow` [10, 20]: **4 trials**; defaults 7 / 10 (the source's).

## Ambiguities resolved

- SMA 100 / 200 are plotted only. Long only, exit on the opposite cross: opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
