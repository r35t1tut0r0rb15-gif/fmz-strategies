# #483121 动态趋势动量交叉策略-基于双重EMA与MACD指标的量化交易系统-Dynamic-Trend-Momentum-Crossover-Strategy-Quantitative-Trading-System-Based-on-Dual-EMA-and-MACD-Indicators -> `fmz_483121_ema12_26_cross_macd_side_2_5pct_bracket_reversal`

- FMZ source id: 483121 (lineage).
- Source: https://www.fmz.com/strategy/483121 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:56:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA crossings with the MACD side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_perc` [2.0, 1.0] x `take_profit_perc` [5.0, 3.0]: **4 trials**; EMA 12 / 26, MACD 12 / 26 / 9.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
