# #482840 指数移动平均线交叉结合动态止损策略-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Loss -> `fmz_482840_ema68_close_cross_always_in_2d`

- FMZ source id: 482840 (lineage).
- Source: https://www.fmz.com/strategy/482840 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:17:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | One EMA; the point stops are inert and dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [68, 34]: **2 trials**; default 68 (the source's). The only parameter that acts.

## Ambiguities resolved

- The point stops never act: `strategy.exit(..., when = close < ema68)` runs only while `is_long`, and the first
  close below the EMA is the crossunder bar, where the short entry (written first) has already set `is_long` false
  (the short side mirrored). Dropped as inert (as #492009); 20 / 10 points on BTC_USDT would be inert anyway.
- REVERSAL INTENDED (always in after the first cross). Two-day bars: blocks of broker-day dates from 1970-01-01
  (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
