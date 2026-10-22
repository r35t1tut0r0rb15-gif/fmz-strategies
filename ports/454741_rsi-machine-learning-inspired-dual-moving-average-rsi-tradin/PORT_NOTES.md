# #454741 机器学习启发的双均线RSI交易策略-Machine-Learning-Inspired-Dual-Moving-Average-RSI-Trading-Strategy -> `fmz_454741_sma10_50_cross_rsi_exit_reversal`

- FMZ source id: 454741 (lineage).
- Source: https://www.fmz.com/strategy/454741 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 15:27:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [50, 100] x `rsi_len` [14, 7]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
