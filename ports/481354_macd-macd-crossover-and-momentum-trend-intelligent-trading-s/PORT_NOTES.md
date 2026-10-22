# #481354 MACD交叉策略与动量趋势智能交易系统-MACD-Crossover-and-Momentum-Trend-Intelligent-Trading-System -> `fmz_481354_macd_signal_cross_long`

- FMZ source id: 481354 (lineage).
- Source: https://www.fmz.com/strategy/481354 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-10 14:44:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9.

## Ambiguities resolved

- Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
