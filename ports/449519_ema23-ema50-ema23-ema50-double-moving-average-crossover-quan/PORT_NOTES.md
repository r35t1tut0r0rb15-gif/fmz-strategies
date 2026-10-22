# #449519 EMA23-EMA50双均线交叉量化交易策略-EMA23-EMA50-Double-Moving-Average-Crossover-Quantitative-Trading-Strategy -> `fmz_449519_ema23_50_cross_stop_test_reentry_reversal`

- FMZ source id: 449519 (lineage).
- Source: https://www.fmz.com/strategy/449519 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 15:29:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close tests against the fill |
| 2 | PASS | EMA crossings with EMA 50 stop tests and trend re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [23, 12] x `slow` [50, 100]: **4 trials**; the 60 % / 25 % targets fixed.

## Ambiguities resolved

- Call order with the held position; start date dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
