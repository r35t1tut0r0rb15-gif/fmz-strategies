# #491514 RSI与SuperTrend过滤策略组合系统趋势确认下的动量反转交易框架-RSI-and-SuperTrend-Filter-Combination-System-Momentum-Reversal-Trading-Framework-with-Trend-Confirmation -> `fmz_491514_rsi14_35_65_cross_band_direction_reversal`

- FMZ source id: 491514 (lineage).
- Source: https://www.fmz.com/strategy/491514 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-21 16:31:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | RSI threshold crossings with a band-direction filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsiOversold` [35, 30] x `atrMult` [3.0, 2.0]: **4 trials** (overbought 100 minus it); RSI 14, ATR 10.

## Ambiguities resolved

- The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`trailing_stop_pending`
