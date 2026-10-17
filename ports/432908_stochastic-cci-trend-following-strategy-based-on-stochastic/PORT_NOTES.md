# #432908 基于Stochastic指标和CCI指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Stochastic-and-CCI -> `fmz_432908_rsi_ema_cci_roc_turn`

- FMZ source id: 432908 (lineage).
- Source: https://www.fmz.com/strategy/432908 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 16:23:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | RSI direction, CCI sign, rate of change and a percentage stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pcnt` [7.0, 3.0] x `sl_pct` [3.0, 6.0]: **4 trials**; CCI 13, RSI 19 / 12 and ROC 30 fixed.

## Ambiguities resolved

- Signal = the state turning (last-time crossovers). Stop live on the fill bar in the house engine. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
