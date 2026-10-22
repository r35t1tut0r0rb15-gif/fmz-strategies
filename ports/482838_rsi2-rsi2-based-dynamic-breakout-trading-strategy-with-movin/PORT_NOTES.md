# #482838 基于RSI2的动态突破交易策略结合移动平均线过滤系统-RSI2-Based-Dynamic-Breakout-Trading-Strategy-with-Moving-Average-Filter-System -> `fmz_482838_rsi2_turn_from_25_sma50_hold5_long`

- FMZ source id: 482838 (lineage).
- Source: https://www.fmz.com/strategy/482838 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:37:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI 2 turn with an SMA filter and a bar-count exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_buy_level` [25.0, 10.0] x `max_bars` [5, 3]: **4 trials**; RSI 2, SMA 50.

## Ambiguities resolved

- The bar count starts at 1 on the signal bar, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
