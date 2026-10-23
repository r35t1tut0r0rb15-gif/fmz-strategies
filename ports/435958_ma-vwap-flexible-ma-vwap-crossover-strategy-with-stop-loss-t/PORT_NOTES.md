# #435958 基于MA-VWAP交叉的灵活止损止盈策略Flexible-MA-VWAP-Crossover-Strategy-with-Stop-Loss-Take-Profit -> `fmz_435958_sma9_vwap14_sma21_double_cross_armed_bracket_long`

- FMZ source id: 435958 (lineage).
- Source: https://www.fmz.com/strategy/435958 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:06:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; late-armed stop / target followed in the signals |
| 2 | PASS | Double moving-average / rolling VWAP crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [9, 5] x `slow_length` [21, 34]: **4 trials**; VWAP 14, SL 1 %, TP 2 %.

## Ambiguities resolved

- Exit armed only by a sell bar; touches close at the next open (signals). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
