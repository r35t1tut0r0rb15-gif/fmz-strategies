# #474631 多周期组合K线形态识别交易策略-Multi-Timeframe-Combined-Candlestick-Pattern-Recognition-Trading-Strategy -> `fmz_474631_ten_candlestick_patterns_reversal`

- FMZ source id: 474631 (lineage).
- Source: https://www.fmz.com/strategy/474631 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 11:04:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candlestick patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the pattern switches all on, the factors constants).

## Ambiguities resolved

- The short wins a bar with both (call order). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
