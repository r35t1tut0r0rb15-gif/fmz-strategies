# #489034 均线交叉空头反转量化策略SMA20-50-智能空单交易系统-SMA20-50-Bearish-Trend-Reversal-Quantitative-Trading-System -> `fmz_489034_sma_20_50_cross_down_short`

- FMZ source id: 489034 (lineage).
- Source: https://www.fmz.com/strategy/489034 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 13:45:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMAs only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; defaults 20 / 50 (the source's).

## Ambiguities resolved

- Short only; the cross up is a close-based exit. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
