# #477973 基于EMA马德里带和唐奇安通道的多模式止盈止损趋势跟踪策略-Multi-Mode-Take-Profit-Stop-Loss-Trend-Following-Strategy-Based-on-EMA-Madrid-Ribbon-and-Donchian-Channel -> `fmz_477973_madrid_donchian20_second_bar_range_bracket_reversal`

- FMZ source id: 477973 (lineage).
- Source: https://www.fmz.com/strategy/477973 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-10 16:24:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Second-bar trend breakouts with a candle-range bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dlen` [20, 55] x `rr` [2.0, 1.0]: **4 trials**; EMA 5 / 100 / 200.

## Ambiguities resolved

- Risk-reward mode (default). Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
