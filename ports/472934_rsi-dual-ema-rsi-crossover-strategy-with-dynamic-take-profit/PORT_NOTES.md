# #472934 双均线RSI交叉动态止盈止损量化策略-Dual-EMA-RSI-Crossover-Strategy-with-Dynamic-Take-Profit-Stop-Loss -> `fmz_472934_ema9_21_cross_rsi_filter_pct_bracket_reversal`

- FMZ source id: 472934 (lineage).
- Source: https://www.fmz.com/strategy/472934 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 11:01:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | EMA crossings with an RSI filter and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `tp_pct` [0.015, 0.03]: **8 trials**; the 1 % stop fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
