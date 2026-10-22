# #485293 Multi Strategy Adaptive Market Condition Trading System -> `fmz_485293_sma10_50_cross_or_bb_rsi_extreme_reversal`

- FMZ source id: 485293 (lineage).
- Source: https://www.fmz.com/strategy/485293 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-07 09:59:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings or band / RSI extremes |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [50, 100]: **4 trials**; RSI 14 / 30 / 70, Bollinger 20 / 2.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
