# #483116 双均线交叉结合RSI动量优化交易策略-Dual-Moving-Average-Crossover-with-RSI-Momentum-Enhancement-Strategy -> `fmz_483116_ema9_21_cross_rsi14_filter_reversal`

- FMZ source id: 483116 (lineage).
- Source: https://www.fmz.com/strategy/483116 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:57:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [9, 5] x `slow_length` [21, 50]: **4 trials**; RSI 14 / 70 / 30.

## Ambiguities resolved

- MPL 2.0 source, ported and stated. REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
