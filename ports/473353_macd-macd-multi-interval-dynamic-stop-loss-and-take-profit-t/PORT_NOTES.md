# #473353 MACD多区间动态止盈止损交易系统-MACD-Multi-Interval-Dynamic-Stop-Loss-and-Take-Profit-Trading-System -> `fmz_473353_macd12_26_9_cross_reversal_long_bracket_from_replaced_avg`

- FMZ source id: 473353 (lineage).
- Source: https://www.fmz.com/strategy/473353 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:01:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | MACD crossings with a long bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.01, 0.02] x `tp_pct` [0.02, 0.04]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- The long's bracket from the replaced short's price (na from flat), as written; no trail (offset only). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
