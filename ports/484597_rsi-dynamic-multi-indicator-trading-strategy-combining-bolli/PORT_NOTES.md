# #484597 融合布林带与RSI的动态多指标交易策略-Dynamic-Multi-Indicator-Trading-Strategy-Combining-Bollinger-Bands-and-RSI -> `fmz_484597_bollinger_reentry_breakout_rolling_bracket_reversal`

- FMZ source id: 484597 (lineage).
- Source: https://www.fmz.com/strategy/484597 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 10:38:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent bracket followed in the signals |
| 2 | PASS | Bollinger re-entries and breakouts |
| 3 | PASS | Exchange pair in the header only (silver named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.03] x `tp` [0.04, 0.06]: **4 trials**; BB 20 x 2, RSI 14, volume SMA 20.

## Ambiguities resolved

- Breakout trades have no exit; the others' rolling bracket is followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
