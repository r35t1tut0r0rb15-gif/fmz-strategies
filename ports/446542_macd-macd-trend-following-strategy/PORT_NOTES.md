# #446542 MACD趋势跟踪策略-MACD-Trend-Following-Strategy -> `fmz_446542_macd3_9_5_signal_zero_state_reversal`

- FMZ source id: 446542 (lineage).
- Source: https://www.fmz.com/strategy/446542 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-29 15:14:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD signal and zero-line state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 12] x `slow` [9, 26]: **4 trials**; the signal length 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
