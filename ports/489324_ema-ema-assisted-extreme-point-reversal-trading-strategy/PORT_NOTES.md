# #489324 EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy -> `fmz_489324_cci10_zero_cross_rsi_extreme_hook_ema100_reversal`

- FMZ source id: 489324 (lineage).
- Source: https://www.fmz.com/strategy/489324 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 14:50:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI zero crossings after RSI extremes with an EMA filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ccimomLength` [10, 20] x `rsiOversold` [35, 25]: **4 trials** (overbought 100 minus it); RSI 14, EMA 100.

## Ambiguities resolved

- ta.cross is either direction, as written. REVERSAL INTENDED. FREQ = "3D" (three broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cci"`.

## Marks

`none`
