# #435713 基于双EMA和价格波动率指标的量化交易策略Quantitative-Trading-Strategy-Based-on-Double-EMA-and-Price-Volatility-Index -> `fmz_435713_ema_channel_range_combo`

- FMZ source id: 435713 (lineage).
- Source: https://www.fmz.com/strategy/435713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 11:26:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel state and a range comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length` [14, 20]: **4 trials**; look-back 20 and range SMA 16 fixed.

## Ambiguities resolved

- Persistent states combined; start date dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
