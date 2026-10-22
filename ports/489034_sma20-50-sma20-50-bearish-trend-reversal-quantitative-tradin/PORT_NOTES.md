# #489034 均线交叉空头反转量化策略SMA20-50-智能空单交易系统-SMA20-50-Bearish-Trend-Reversal-Quantitative-Trading-System -> `fmz_489034_sma20_50_cross_short`

- FMZ source id: 489034 (lineage).
- Source: https://www.fmz.com/strategy/489034 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 13:45:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 5000, 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Short only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
