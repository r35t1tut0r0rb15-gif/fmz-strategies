# #482832 双均线交叉结合RSI强弱过滤交易策略-Dual-Moving-Average-Crossover-with-RSI-Strength-Filter-Trading-Strategy -> `fmz_482832_ema5_sma10_cross_rsi14_50_exit_flag_long`

- FMZ source id: 482832 (lineage).
- Source: https://www.fmz.com/strategy/482832 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:50:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The close-vs-RSI test read at the header's prices (always passes; no shorts) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 8] x `slow` [10, 20]: **4 trials**; RSI 14, exit level 50.

## Ambiguities resolved

- The close-vs-RSI comparison is read at ETH prices: always true for the buy, never for the sell (no shorts).
- The flag loop keeps a long whose close was called before it filled. Long only. FREQ = "3D" (three broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
