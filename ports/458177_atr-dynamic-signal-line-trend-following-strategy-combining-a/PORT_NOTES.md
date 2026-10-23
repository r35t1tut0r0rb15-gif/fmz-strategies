# #458177 ATR和交易量结合的动态信号线趋势跟踪策略-Dynamic-Signal-Line-Trend-Following-Strategy-Combining-ATR-and-Volume -> `fmz_458177_atr_signal_line_cross_volume_prev_bar_exit_1h_reversal`

- FMZ source id: 458177 (lineage).
- Source: https://www.fmz.com/strategy/458177 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:01:40). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Signal-line crossings of the low / high on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100] x `offset` [1, 2]: **4 trials**; ATR 20, volume x 1.5.

## Ambiguities resolved

- Closes act from the bar after the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
