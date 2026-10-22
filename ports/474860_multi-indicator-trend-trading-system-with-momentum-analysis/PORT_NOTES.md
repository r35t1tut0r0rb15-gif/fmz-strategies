# #474860 Multi Indicator Trend Trading System with Momentum Analysis Strategy -> `fmz_474860_sma200_stochrsi_as_written_macd_state_sma50_exit_reversal`

- FMZ source id: 474860 (lineage).
- Source: https://www.fmz.com/strategy/474860 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:53:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend / momentum states with SMA 50 closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths constants).

## Ambiguities resolved

- The stochastic call's arguments as written (constant low 14, length 3). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
