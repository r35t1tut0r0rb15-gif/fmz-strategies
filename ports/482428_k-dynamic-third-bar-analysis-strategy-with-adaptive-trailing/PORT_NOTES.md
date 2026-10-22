# #482428 动态跟踪止损的三分之一K线量化交易策略-Dynamic-Third-Bar-Analysis-Strategy-with-Adaptive-Trailing-Stop -> `fmz_482428_trinity_bar_thirds_sequence_daily_reversal`

- FMZ source id: 482428 (lineage).
- Source: https://www.fmz.com/strategy/482428 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 13:57:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the bar-low trailing stop described (pending) |
| 2 | PASS | Bar-thirds continuation sequences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND482242. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the trailing stop pending).

## Ambiguities resolved

- The previous-bar trailing stop is kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
