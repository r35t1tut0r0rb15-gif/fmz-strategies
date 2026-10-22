# #474862 多重均线趋势追踪与SMMA验证交易策略-Multi-EMA-Trend-Following-Strategy-with-SMMA-Confirmation -> `fmz_474862_ema10_22_cross_smma200_filter_reversal`

- FMZ source id: 474862 (lineage).
- Source: https://www.fmz.com/strategy/474862 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:55:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a long-average filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `long_len` [22, 50]: **4 trials**; filter 200.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
