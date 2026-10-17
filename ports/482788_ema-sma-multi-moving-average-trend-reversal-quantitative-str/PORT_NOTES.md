# #482788 多均线趋势反转量化策略基于EMA和SMA的组合信号系统-Multi-Moving-Average-Trend-Reversal-Quantitative-Strategy-Combined-EMA-and-SMA-Signal-System -> `fmz_482788_sma50_200_cross_always_in`

- FMZ source id: 482788 (lineage).
- Source: https://www.fmz.com/strategy/482788 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:49:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Two SMAs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; defaults 50 / 200 (the source's).

## Ambiguities resolved

- The EMA 9 / 21 crosses and pivots feed only drawings and alerts. REVERSAL INTENDED (always in). FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
