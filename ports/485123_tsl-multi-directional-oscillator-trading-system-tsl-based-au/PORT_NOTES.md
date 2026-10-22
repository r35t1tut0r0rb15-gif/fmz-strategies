# #485123 多重摆动指标交易系统基于TSL自动化多方向仓位管理策略-Multi-Directional-Oscillator-Trading-System-TSL-Based-Automated-Position-Management-Strategy -> `fmz_485123_swing3_tsl_cross_reversal`

- FMZ source id: 485123 (lineage).
- Source: https://www.fmz.com/strategy/485123 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 10:57:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing trailing-level crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Quantity 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [3, 5, 10]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
