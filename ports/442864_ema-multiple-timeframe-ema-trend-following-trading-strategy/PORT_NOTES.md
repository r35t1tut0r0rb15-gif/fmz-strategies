# #442864 多周期EMA顺势突破交易策略Multiple-Timeframe-EMA-Trend-Following-Trading-Strategy -> `fmz_442864_ema12_24_ribbon_order_reversal`

- FMZ source id: 442864 (lineage).
- Source: https://www.fmz.com/strategy/442864 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 16:55:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMA ribbon |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [12, 6] x `step` [3, 5]: **4 trials** (five EMAs start + step x 0..4).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
