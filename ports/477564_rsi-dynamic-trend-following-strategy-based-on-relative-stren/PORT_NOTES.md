# #477564 基于相对强弱与RSI的动态趋势跟踪套利策略-Dynamic-Trend-Following-Strategy-Based-on-Relative-Strength-and-RSI -> `fmz_477564_rs55_off_low_rsi60_avg_stop_long`

- FMZ source id: 477564 (lineage).
- Source: https://www.fmz.com/strategy/477564 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 14:02:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price stop as a fraction of the fill |
| 2 | PASS | RSI strength off the range low, as written (SuperTrend outputs swapped) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop percentage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rs_period` [55, 20] x `rsi_threshold` [60.0, 50.0]: **4 trials**; RSI 14, stop 2 %.

## Ambiguities resolved

- SuperTrend outputs swapped in the script: its trend tests always pass or never fire, as written.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
