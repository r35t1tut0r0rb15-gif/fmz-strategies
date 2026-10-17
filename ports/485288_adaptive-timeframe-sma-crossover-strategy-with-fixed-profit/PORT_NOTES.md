# #485288 均线突破固定利润目标自适应时间周期量化交易策略-Adaptive-Timeframe-SMA-Crossover-Strategy-with-Fixed-Profit-Targets -> `fmz_485288_sma20_cross_one_bar_hold`

- FMZ source id: 485288 (lineage).
- Source: https://www.fmz.com/strategy/485288 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-07 09:49:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; one-bar holds as written. |
| 2 | PASS | A moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [20, 50]: **2 trials**; default 20 (the source's). The other inputs (the 20-point target, the timeframe
list) have no effect as written.

## Ambiguities resolved

- `timeframe.period` on the 5-hour header chart is not in "1,3,5", so `close_all` fires on every bar; it acts on the
  position at the bar's start (#430850): every trade closes on the bar after its fill; an opposite signal there
  reverses (REVERSAL INTENDED). The 20-point target can only fire together with `close_all`: redundant.
- Five-hour bins restart each UTC day (00, 05, 10, 15, 20 h), as a 24-hour chart does (decision owed if the house
  wants another anchoring). FREQ = "5h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
