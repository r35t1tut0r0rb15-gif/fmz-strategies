# #453645 10SMA与MACD双重趋势跟踪交易策略-10SMA-and-MACD-Dual-Trend-Following-Trading-Strategy -> `fmz_453645_close_sma10_and_macd_joint_cross_long`

- FMZ source id: 453645 (lineage).
- Source: https://www.fmz.com/strategy/453645 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 14:46:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Joint SMA / MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `fast` [12, 8] x `slow` [26, 21]: **8 trials**; the signal 9 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
