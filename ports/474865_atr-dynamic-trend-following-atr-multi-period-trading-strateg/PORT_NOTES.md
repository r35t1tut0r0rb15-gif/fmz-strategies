# #474865 动态趋势跟踪ATR多周期交易策略-Dynamic-Trend-Following-ATR-Multi-Period-Trading-Strategy -> `fmz_474865_ut_bot_atr3_key9_trail_cross_reversal`

- FMZ source id: 474865 (lineage).
- Source: https://www.fmz.com/strategy/474865 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 16:00:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing-line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed quantities stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG474865. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [9, 3] x `atr_period` [3, 10]: **4 trials**; close source.

## Ambiguities resolved

- The id juggling reduces to a reversal (pyramiding 1). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
