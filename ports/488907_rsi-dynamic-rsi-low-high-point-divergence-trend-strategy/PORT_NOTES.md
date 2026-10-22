# #488907 动态RSI低高点背离趋势策略-Dynamic-RSI-Low-High-Point-Divergence-Trend-Strategy -> `fmz_488907_rsi14_divergence_10bar_extreme_reversal`

- FMZ source id: 488907 (lineage).
- Source: https://www.fmz.com/strategy/488907 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 17:24:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price / RSI divergence at extremes |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `oversold` [30, 40]: **4 trials** (overbought 100 minus it); RSI 14.

## Ambiguities resolved

- No exits; REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_divergence"`.

## Marks

`none`
