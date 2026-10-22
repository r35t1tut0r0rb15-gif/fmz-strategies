# #483037 多重指标趋势跟踪策略基于SMA双线交叉结合RSI和ADX的动态波动率优化系统-Multi-Indicator-Trend-Following-Strategy-SMA-Dual-Line-Crossover-with-RSI-and-ADX-Dynamic-Volatility-Optimization-System -> `fmz_483037_sma10_200_cross_rsi50_adx20_tick_trail_reversal`

- FMZ source id: 483037 (lineage).
- Source: https://www.fmz.com/strategy/483037 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:15:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | ADAPT | Tick trail read as percents at the header's ETH prices |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [1.852e-05, 0.005] x `sma_fast` [10, 20]: **4 trials**; activate after 6 x trail_pct (30 / 5 ticks), SMA 200, RSI 14 / 50, ADX 14 over 20.

## Ambiguities resolved

- Tick trail read at the header's ETH_USDT prices (about 2700). REVERSAL INTENDED. FREQ = "4min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
