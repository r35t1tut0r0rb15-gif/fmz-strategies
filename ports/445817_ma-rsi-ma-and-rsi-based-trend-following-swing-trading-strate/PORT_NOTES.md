# #445817 基于MA和RSI的趋势跟踪摆动策略MA-and-RSI-based-Trend-Following-Swing-Trading-Strategy -> `fmz_445817_sma50_200_cross_rsi_filter_pct_bracket_reversal`

- FMZ source id: 445817 (lineage).
- Source: https://www.fmz.com/strategy/445817 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 14:31:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-sent levels marked) |
| 2 | PASS | SMA crossings with close and RSI filters, percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.01] x `rr` [2.0, 3.0]: **4 trials**; the SMA and RSI lengths and levels fixed.

## Ambiguities resolved

- Percent bracket from the fill; repeat-signal moves not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
