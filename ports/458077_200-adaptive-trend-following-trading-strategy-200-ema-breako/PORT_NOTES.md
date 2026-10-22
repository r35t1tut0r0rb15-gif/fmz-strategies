# #458077 自适应趋势跟踪交易策略200均线突破与动态风险管理系统-Adaptive-Trend-Following-Trading-Strategy-200-EMA-Breakout-with-Dynamic-Risk-Management-System -> `fmz_458077_ema200_close_cross_pct_bracket_reversal`

- FMZ source id: 458077 (lineage).
- Source: https://www.fmz.com/strategy/458077 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:11:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | EMA 200 crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `sl_pct` [0.01, 0.03] x `tp_pct` [0.02, 0.06]: **8 trials**.

## Ambiguities resolved

- Bracket as fractions of the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
