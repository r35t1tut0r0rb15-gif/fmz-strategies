# #439243 基于均线和RSI的机会跟踪策略EMA-Hull-and-RSI-Opportunity-Tracking-Strategy -> `fmz_439243_hull_ema50_cross_rsi_filter`

- FMZ source id: 439243 (lineage).
- Source: https://www.fmz.com/strategy/439243 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 15:46:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull / EMA crossings and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `hull_len` [7, 14]: **4 trials**; RSI 14 and the 60 / 45 levels fixed.

## Ambiguities resolved

- Pine rounding in the Hull. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
