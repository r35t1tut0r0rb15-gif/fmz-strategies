# #483515 24小时量价结合斐波那契回调交叉均线交易策略-24-Hour-Volume-Price-Fibonacci-Retracement-MA-Cross-Trading-Strategy -> `fmz_483515_sma14_28_cross_reversal`

- FMZ source id: 483515 (lineage).
- Source: https://www.fmz.com/strategy/483515 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:55:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 14 / 28 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 10] x `slow` [28, 50]: **4 trials**.

## Ambiguities resolved

- Fibonacci and volume only plot. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
