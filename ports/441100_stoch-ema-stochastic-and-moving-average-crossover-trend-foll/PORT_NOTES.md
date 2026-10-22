# #441100 基于Stoch和EMA指标的趋势跟踪量化策略Stochastic-and-Moving-Average-Crossover-Trend-Following-Quantitative-Strategy -> `fmz_441100_stoch_zone_cross_ema_trend_pct_target`

- FMZ source id: 441100 (lineage).
- Source: https://www.fmz.com/strategy/441100 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-05 15:27:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target from the close -> fixed fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.08, 0.04] x `stoch_length` [14, 9]: **4 trials**; EMAs, smoothing and levels fixed.

## Ambiguities resolved

- Tick target as a fixed fraction. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
