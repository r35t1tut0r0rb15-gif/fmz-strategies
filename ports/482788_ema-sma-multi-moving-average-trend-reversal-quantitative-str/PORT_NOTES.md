# #482788 多均线趋势反转量化策略基于EMA和SMA的组合信号系统-Multi-Moving-Average-Trend-Reversal-Quantitative-Strategy-Combined-EMA-and-SMA-Signal-System -> `fmz_482788_sma50_200_cross_reversal`

- FMZ source id: 482788 (lineage).
- Source: https://www.fmz.com/strategy/482788 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:49:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 50 / 200 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
