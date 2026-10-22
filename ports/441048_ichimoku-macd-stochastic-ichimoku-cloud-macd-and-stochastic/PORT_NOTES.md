# #441048 基于Ichimoku云图MACD和Stochastic的多时间框架趋势跟踪策略Ichimoku-Cloud-MACD-and-Stochastic-Based-Multi-Timeframe-Trend-Tracking-Strategy -> `fmz_441048_ichimoku_macd_stoch_atr_bracket`

- FMZ source id: 441048 (lineage).
- Source: https://www.fmz.com/strategy/441048 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 10:30:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | Cloud, MACD, stochastic and SMA filters with ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.0, 2.0] x `tp_mult` [1.0, 2.0]: **4 trials**; the indicator lengths fixed.

## Ambiguities resolved

- Bracket active from the fill bar (the script's from the fill bar's close). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop`
