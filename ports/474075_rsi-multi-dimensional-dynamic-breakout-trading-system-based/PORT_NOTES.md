# #474075 基于布林带和RSI的多维度动态突破交易系统-Multi-Dimensional-Dynamic-Breakout-Trading-System-Based-on-Bollinger-Bands-and-RSI -> `fmz_474075_bb20_breakout_rsi50_signal_close_bracket_reversal`

- FMZ source id: 474075 (lineage).
- Source: https://www.fmz.com/strategy/474075 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 17:32:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Band breakouts with an RSI filter and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5] x `rr` [2.0, 1.0]: **8 trials**; the stop 2 %.

## Ambiguities resolved

- Repeat-signal re-stores not followed (trailing_stop_pending). Direction Both. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
