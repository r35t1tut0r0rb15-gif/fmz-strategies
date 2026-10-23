# #488138 多层次技术指标动量交易策略基于增强型MACD交易量强度和EMA信号系统-Multi-Level-Technical-Indicator-Momentum-Trading-Strategy-Based-on-Enhanced-MACD-Volume-Strength-and-EMA-Signal-System -> `fmz_488138_ema9_26_or_volume_macd_cross_1h_reversal`

- FMZ source id: 488138 (lineage).
- Source: https://www.fmz.com/strategy/488138 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 14:04:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings or volume-confirmed MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [26, 34]: **4 trials**; signal 9, volume SMA 20.

## Ambiguities resolved

- The later short wins on a two-sided bar. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
