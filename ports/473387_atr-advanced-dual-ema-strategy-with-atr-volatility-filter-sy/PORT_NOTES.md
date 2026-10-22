# #473387 高级双均线策略与ATR波动率过滤系统-Advanced-Dual-EMA-Strategy-with-ATR-Volatility-Filter-System -> `fmz_473387_ema50_200_cross_atr_filter_reversal`

- FMZ source id: 473387 (lineage).
- Source: https://www.fmz.com/strategy/473387 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:14:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an ATR filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100] x `atr_threshold` [0.02, 2.0]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
