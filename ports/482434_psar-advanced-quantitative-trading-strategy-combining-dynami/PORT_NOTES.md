# #482434 动态布林带结合PSAR指标的高级量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-Dynamic-Bollinger-Bands-with-PSAR-Indicator -> `fmz_482434_bb20_breakout_body_third_window_3r_bracket_reversal`

- FMZ source id: 482434 (lineage).
- Source: https://www.fmz.com/strategy/482434 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:11:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar candle bracket as fractions of the fill |
| 2 | PASS | Bollinger breakouts by full-bodied candles in a time window |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `rr` [3.0, 2.0]: **4 trials**; 2 sd, body 1/3, window 07:30-16:00 GMT-5.

## Ambiguities resolved

- Fixed GMT-5 window (no DST). Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
