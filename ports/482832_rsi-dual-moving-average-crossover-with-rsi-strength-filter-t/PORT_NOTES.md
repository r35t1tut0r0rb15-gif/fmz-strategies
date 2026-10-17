# #482832 双均线交叉结合RSI强弱过滤交易策略-Dual-Moving-Average-Crossover-with-RSI-Strength-Filter-Trading-Strategy -> `fmz_482832_ema5_sma10_cross_rsi50_exit_long_3d`

- FMZ source id: 482832 (lineage).
- Source: https://www.fmz.com/strategy/482832 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:50:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An EMA, an SMA and RSI levels; the price-vs-RSI filters are inert and dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [10, 20] x `rsi_exit` [50, 40]: **4 trials**; defaults 10 / 50 (the source's); EMA 5 and RSI 14 fixed.

## Ambiguities resolved

- The filters compare the close with the RSI value. On ETH_USDT the close is always above it: the long filter always
  passes and the short entry (allowed only when close <= RSI) never fires. Both are dropped as inert (as #492009,
  #490798); the port is long only, and the short close test goes with the short side.
- `active_buy` is kept as written: it blocks a new cross while set and is cleared by the close test even on the
  entry's own bar (the close cannot undo the entry there, #430850).
- Three-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
