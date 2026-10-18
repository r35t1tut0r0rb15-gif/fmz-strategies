# #436502 Dynamic Moving Averages and Keltner Channel Trading Strategy -> `fmz_436502_breakout_bar_ma_side`

- FMZ source id: 436502 (lineage).
- Source: https://www.fmz.com/strategy/436502 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-25 13:36:40). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Breakout bar and moving-average side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["SMA", "EMA"] x `length` [20, 50]: **4 trials**.

## Ambiguities resolved

- SMA and EMA lengths share one grid value (both default 20). Orders in call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
