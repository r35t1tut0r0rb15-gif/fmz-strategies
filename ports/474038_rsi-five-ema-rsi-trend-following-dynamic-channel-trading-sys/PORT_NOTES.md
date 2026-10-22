# #474038 五均线RSI趋势跟踪动态通道交易系统-Five-EMA-RSI-Trend-Following-Dynamic-Channel-Trading-System -> `fmz_474038_ema9_55_cross_rsi60_40_signal_bar_bracket_reversal`

- FMZ source id: 474038 (lineage).
- Source: https://www.fmz.com/strategy/474038 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 15:15:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with RSI confirmation and a signal-bar bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [55, 100]: **4 trials**; RSI levels and the bracket factors fixed.

## Ambiguities resolved

- TP2 never fills before TP1 (full-size exits). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
