# #445802 基于ATR双重跟踪止损的动态止盈止损策略Dynamic-Stop-Loss-and-Take-Profit-Strategy-Based-on-Dual-ATR-Trailing-Stop -> `fmz_445802_ut_bot_two_lines_cross_reversal`

- FMZ source id: 445802 (lineage).
- Source: https://www.fmz.com/strategy/445802 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 13:52:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long target re-sent (mark); the short's wrong-side target read as a close |
| 2 | PASS | UT Bot trailing-line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key1` [1.0, 2.0] x `key2` [2.0, 3.0]: **4 trials**; the ATR periods fixed.

## Ambiguities resolved

- Shorts close at the next open after their fill (Pine may fill that wrong-side limit at the fill open itself). Long target pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`trailing_stop_pending`
