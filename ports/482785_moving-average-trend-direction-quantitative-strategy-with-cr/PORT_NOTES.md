# #482785 移动均线趋势向量量化交易策略-Moving-Average-Trend-Direction-Quantitative-Strategy-with-Cross-Validation -> `fmz_482785_open_close_sma_cross_htf3_always_in`

- FMZ source id: 482785 (lineage).
- Source: https://www.fmz.com/strategy/482785 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:49:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the higher timeframe without look-ahead. |
| 2 | PASS | SMAs of opens and closes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_res` [True, False] x `basis_len` [8, 14]: **4 trials**; defaults True / 8 (the source's); resolution x 3 fixed.

## Ambiguities resolved

- `request.security(..., lookahead_on)` on the 3D resolution reads each 3D bar's final value on every daily bar of
  it (look-ahead on history). House rule (#490787): only the last completed 3D block, i.e. from the first daily bar
  of the next block. 3D blocks: broker-day dates from 1970-01-01 (decision owed, #426509).
- "SMMA" is `ta.sma` in this script. SL / TP points are 0 (off). REVERSAL INTENDED (always in).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
