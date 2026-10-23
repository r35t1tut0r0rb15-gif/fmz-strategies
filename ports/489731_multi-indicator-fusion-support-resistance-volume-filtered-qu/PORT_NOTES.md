# #489731 Multi Indicator Fusion Support Resistance Volume Filtered Quantitative Trading Strategy -> `fmz_489731_near_30d_support_resistance_rsi_volume_reversal`

- FMZ source id: 489731 (lineage).
- Source: https://www.fmz.com/strategy/489731 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-08 09:46:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oversold closes near support and overbought closes near resistance on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sr_window` [30, 20] x `near_pct` [2.0, 1.0]: **4 trials**; RSI 14 30 / 70, volume SMA 20.

## Ambiguities resolved

- Windows include the current bar; no exit. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_reversion"`.

## Marks

`none`
