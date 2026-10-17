# #482861 多维度动态ICT交易策略结合吞没形态与供需区域分析系统-Multi-Dimensional-Dynamic-ICT-Trading-Strategy-with-Engulfing-Patterns-and-Supply-Demand-Zone-Analysis-System -> `fmz_482861_engulfing_zone_pct_bracket`

- FMZ source id: 482861 (lineage).
- Source: https://www.fmz.com/strategy/482861 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:44:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Candle patterns, rolling extremes and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.5, 1.0] x `tp_pct` [3.0, 2.0]: **4 trials**; defaults 1.5 / 3 (the source's); zones of 20 bars on.

## Trailing stop (mark `trailing_stop_pending`)

A later same-side engulfing signal while held re-places the stop and target. The port keeps the entry's bracket.

## Ambiguities resolved

- The zone filters almost always hold, as written; the timeframe input is unused.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick"`.

## Marks

`trailing_stop_pending`
