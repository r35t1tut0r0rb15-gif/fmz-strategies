# #436241 金叉死叉双均线MACD趋势追踪策略Golden-Cross-Dead-Cross-Dual-Moving-Average-MACD-Trend-Tracking-Strategy -> `fmz_436241_triple_ma_cross_macd_bracket`

- FMZ source id: 436241 (lineage).
- Source: https://www.fmz.com/strategy/436241 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 14:17:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick amounts -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.0125, 0.5] x `slow1` [85, 60]: **4 trials**; WMA 75, EMA 5 and MACD 12 / 26 / 9 fixed; the target is 3 x the stop.

## Ambiguities resolved

- Same-bar double cross; tick amounts -> ATR multiples. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
