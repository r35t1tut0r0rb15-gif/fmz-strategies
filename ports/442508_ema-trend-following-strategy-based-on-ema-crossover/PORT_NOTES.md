# #442508 基于EMA平均线交叉的趋势追踪策略Trend-Following-Strategy-Based-on-EMA-Crossover -> `fmz_442508_ema21_55_trend_atr_stop_long`

- FMZ source id: 442508 (lineage).
- Source: https://www.fmz.com/strategy/442508 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 13:59:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | EMA stack and close position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 10] x `slow` [55, 100]: **4 trials**; the ATR length and multiple fixed.

## Ambiguities resolved

- Stop from the signal bar, re-based on the fill. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
