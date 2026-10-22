# #482593 自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy -> `fmz_482593_bb20_reentry_close_atr3_trail_line_exit_reversal`

- FMZ source id: 482593 (lineage).
- Source: https://www.fmz.com/strategy/482593 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:00:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based trailing exits in the loop |
| 2 | PASS | Band re-entries with an ATR trailing exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [3.0, 2.0] x `bb_length` [20, 50]: **4 trials**; BB x 2.0, ATR 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
