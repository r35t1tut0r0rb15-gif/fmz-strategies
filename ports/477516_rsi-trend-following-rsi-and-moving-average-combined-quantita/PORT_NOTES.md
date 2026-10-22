# #477516 趋势跟踪型RSI与移动平均线组合量化交易策略-Trend-Following-RSI-and-Moving-Average-Combined-Quantitative-Trading-Strategy -> `fmz_477516_sma50_side_rsi55_45_pct_bracket_reversal`

- FMZ source id: 477516 (lineage).
- Source: https://www.fmz.com/strategy/477516 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 10:58:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | SMA side with RSI thresholds and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 and capital 50000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [50, 100] x `tp_pct` [0.02, 0.04]: **4 trials**; RSI 14 / 55 / 45, stop 1 %.

## Ambiguities resolved

- State entries repeat while they hold. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
