# #440809 基于布林带RSI和移动平均线的趋势跟踪策略Trend-Following-Strategy-Based-on-Bollinger-Bands-RSI-and-Moving-Average -> `fmz_440809_rsi_momentum_widening_bands_ma_exit`

- FMZ source id: 440809 (lineage).
- Source: https://www.fmz.com/strategy/440809 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 11:35:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels, deviation slope and SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [50, 20] x `overbought` [70, 60]: **4 trials**; oversold = 100 - overbought.

## Ambiguities resolved

- Written order of closes and entries kept. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
