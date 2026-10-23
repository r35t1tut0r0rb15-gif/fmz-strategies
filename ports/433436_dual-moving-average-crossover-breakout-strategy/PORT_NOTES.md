# #433436 Dual Moving Average Crossover Breakout Strategy -> `fmz_433436_ema30_ema33_cross_daily_reversal`

- FMZ source id: 433436 (lineage).
- Source: https://www.fmz.com/strategy/433436 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-27 16:21:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1000000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [30, 20] x `slow_len` [33, 50]: **4 trials**.

## Ambiguities resolved

- Volume sums unused (commented-out VWEMAs). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
