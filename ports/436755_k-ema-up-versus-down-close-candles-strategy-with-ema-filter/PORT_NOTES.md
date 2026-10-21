# #436755 基于K线收盘价多空比较与EMA过滤的量化交易策略Up-versus-Down-Close-Candles-Strategy-with-EMA-filter-and-Session-Timeframes -> `fmz_436755_up_down_close_count_sessions`

- FMZ source id: 436755 (lineage).
- Source: https://www.fmz.com/strategy/436755 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 14:38:28). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Close counts and EMA side inside fixed UTC clock windows |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 30] x `ema_period` [50, 100]: **4 trials**; the two UTC windows fixed.

## Ambiguities resolved

- Session strings read in UTC (the backtest exchange's zone); redundant closes dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
