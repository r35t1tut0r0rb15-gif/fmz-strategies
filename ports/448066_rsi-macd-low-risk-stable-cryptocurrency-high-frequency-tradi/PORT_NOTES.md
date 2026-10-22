# #448066 基于RSI和MACD的低风险稳健型加密货币高频交易策略-Low-Risk-Stable-Cryptocurrency-High-Frequency-Trading-Strategy-Based-on-RSI-and-MACD -> `fmz_448066_sma9_21_cross_rsi_macd_confirm_long`

- FMZ source id: 448066 (lineage).
- Source: https://www.fmz.com/strategy/448066 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-12 16:54:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA cross-ups with RSI and MACD confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the RSI and MACD settings fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
