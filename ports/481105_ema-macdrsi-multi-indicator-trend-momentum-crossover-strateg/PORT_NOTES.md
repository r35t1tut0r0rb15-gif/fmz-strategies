# #481105 多指标趋势动量交叉策略EMA双均线与MACDRSI协同信号系统-Multi-Indicator-Trend-Momentum-Crossover-Strategy-EMA-Dual-Moving-Average-with-MACD-RSI-Synergy-System -> `fmz_481105_ema12_26_macd_joint_cross_rsi_long`

- FMZ source id: 481105 (lineage).
- Source: https://www.fmz.com/strategy/481105 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 15:15:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Joint EMA and MACD crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`signal_len` [9, 5] x `rsi_high` [70, 80]: **4 trials**; EMA 12 / 26, RSI 14.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
