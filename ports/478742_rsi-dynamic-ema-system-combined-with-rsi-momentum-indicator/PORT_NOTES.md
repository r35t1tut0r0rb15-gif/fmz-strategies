# #478742 动态均线系统结合RSI动量指标的日内交易优化策略-Dynamic-EMA-System-Combined-with-RSI-Momentum-Indicator-for-Optimized-Intraday-Trading-Strategy -> `fmz_478742_ema12_26_cross_rsi50_pct_bracket_reversal`

- FMZ source id: 478742 (lineage).
- Source: https://www.fmz.com/strategy/478742 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:27:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter, a percent bracket and crossing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 20 / close stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 5] x `slow` [26, 50]: **4 trials**; RSI 14, stop 1 %, target 2 %.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
