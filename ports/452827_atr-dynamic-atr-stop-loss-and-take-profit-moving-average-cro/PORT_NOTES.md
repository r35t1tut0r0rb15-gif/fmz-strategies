# #452827 动态ATR止盈止损移动均线交叉策略-Dynamic-ATR-Stop-Loss-and-Take-Profit-Moving-Average-Crossover-Strategy -> `fmz_452827_sma10_50_cross_hour_window_atr_bracket_long`

- FMZ source id: 452827 (lineage).
- Source: https://www.fmz.com/strategy/452827 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:19:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long bracket as ATR fractions of the signal close; the zero-length short read as a close |
| 2 | PASS | SMA crossings in a UTC hour window |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the risk input is unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [50, 100] x `sl_atr` [1.5, 1.0]: **8 trials**; the 3 ATR target and the hour window fixed.

## Ambiguities resolved

- Session on the UTC open hour; the short is zero-length (sent as the long's exit). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
