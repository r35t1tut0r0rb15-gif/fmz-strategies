# #483674 交叉动能趋势跟踪策略SMA-RSI交叉动量系统-Cross-Momentum-Trend-Following-Strategy-SMA-RSI-Cross-Momentum-System -> `fmz_483674_close_sma20_cross_rsi8_60_40_long`

- FMZ source id: 483674 (lineage).
- Source: https://www.fmz.com/strategy/483674 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-25 10:44:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [20, 50] x `rsi_length` [8, 14]: **4 trials**; levels 60 / 40.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
