# #439710 基于ATR和RSI的自适应移动止损趋势跟踪策略Adaptive-ATR-and-RSI-Trend-Following-Strategy-with-Trailing-Stop-Loss -> `fmz_439710_ut_bot_atr_trail_cross`

- FMZ source id: 439710 (lineage).
- Source: https://www.fmz.com/strategy/439710 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-23 11:31:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435835. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [10, 2] x `c` [10, 14]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
