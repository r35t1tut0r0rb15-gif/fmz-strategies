# #452716 基于ATR和EMA的动态止盈止损自适应策略-ATR-and-EMA-based-Dynamic-Take-Profit-and-Stop-Loss-Adaptive-Strategy -> `fmz_452716_ut_bot_atr_line_cross_reversal`

- FMZ source id: 452716 (lineage).
- Source: https://www.fmz.com/strategy/452716 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 14:15:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | UT Bot line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_len` [10, 14]: **4 trials**.

## Ambiguities resolved

- The exits name never-entered ids. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
