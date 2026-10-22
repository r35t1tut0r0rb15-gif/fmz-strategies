# #484773 动态ATR追踪止损交易策略市场波动性自适应系统-Dynamic-ATR-Trailing-Stop-Trading-Strategy-Market-Volatility-Adaptive-System -> `fmz_484773_atr10_flip_line_cross_reversal`

- FMZ source id: 484773 (lineage).
- Source: https://www.fmz.com/strategy/484773 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-04 11:03:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR line crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key_value` [1.0, 2.0] x `atr_period` [10, 20]: **4 trials**.

## Ambiguities resolved

- The unratcheted line is kept as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
