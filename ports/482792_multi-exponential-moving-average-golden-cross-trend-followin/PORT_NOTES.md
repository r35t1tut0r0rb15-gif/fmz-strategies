# #482792 多重指数移动平均线黄金交叉趋势跟踪策略-Multi-Exponential-Moving-Average-Golden-Cross-Trend-Following-Strategy -> `fmz_482792_ema20_50_cross_long`

- FMZ source id: 482792 (lineage).
- Source: https://www.fmz.com/strategy/482792 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:48:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Two EMAs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; commission and slippage are costs. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; defaults 20 / 50 (the source's).

## Ambiguities resolved

- The crosses alternate, so the position tests change nothing. The EMA 150 crosses only feed drawings.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
