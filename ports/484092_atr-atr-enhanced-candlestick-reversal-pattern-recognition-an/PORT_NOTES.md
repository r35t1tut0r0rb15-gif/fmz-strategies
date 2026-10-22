# #484092 ATR增强型蜡烛反转模式识别与风险管理策略-ATR-Enhanced-Candlestick-Reversal-Pattern-Recognition-and-Risk-Management-Strategy -> `fmz_484092_hammer_star_atr1_5_range_open_cross_reversal`

- FMZ source id: 484092 (lineage).
- Source: https://www.fmz.com/strategy/484092 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:48:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | Hammer / shooting-star candles with an ATR range filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 2 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 1.0] x `atr_length` [14, 20]: **4 trials**.

## Ambiguities resolved

- The per-bar bracket is pending, not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
