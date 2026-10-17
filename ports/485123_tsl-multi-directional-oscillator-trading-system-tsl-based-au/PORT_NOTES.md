# #485123 多重摆动指标交易系统基于TSL自动化多方向仓位管理策略-Multi-Directional-Oscillator-Trading-System-TSL-Based-Automated-Position-Management-Strategy -> `fmz_485123_swing_tsl_cross`

- FMZ source id: 485123 (lineage).
- Source: https://www.fmz.com/strategy/485123 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 10:57:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty 1 quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [3, 5]: **2 trials**; default 3 (the source's only trading input).

## Ambiguities resolved

- `avn` (the last non-zero `avd`) is na until the first breakout; then the line is the 3-bar high, as written. The
  close after each entry is the reversal (REVERSAL INTENDED). The open-trade price tracking only feeds labels. Daily
  bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "swing_breakout"`.

## Marks

`none`
