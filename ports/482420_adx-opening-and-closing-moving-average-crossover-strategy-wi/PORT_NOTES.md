# #482420 开盘收盘均线交叉结合ADX动态指标的量化交易策略-Opening-and-Closing-Moving-Average-Crossover-Strategy-with-ADX-Dynamic-Indicator -> `fmz_482420_open_close_sma_cross_htf9_adx_3d`

- FMZ source id: 482420 (lineage).
- Source: https://www.fmz.com/strategy/482420 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:35:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the higher timeframe without look-ahead. |
| 2 | PASS | SMAs of opens and closes and an ADX variant. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_res` [True, False] x `adx_filter` [13, 20]: **4 trials**; defaults True / 13 (the source's); resolution x 3,
SMA 8 and ADX 14 fixed.

## Ambiguities resolved

- `request.security(..., lookahead_on)` on 9D (3 x the 3D chart): only the last completed 9-day block (house rule,
  #490787), as #482785. Blocks: broker-day dates from 1970-01-01 (decision owed, #426509).
- DM zeroing sequential and the true range double-smoothed (ATR then RMA), as written. SL / TP points 0 (off).
- REVERSAL INTENDED (always in). FREQ = "3D".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
