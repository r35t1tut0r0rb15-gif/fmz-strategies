# #446549 EMA-MACD-SuperTrend-ADX-ATR多重指标交易信号策略-EMA-MACD-SuperTrend-ADX-ATR-Multi-Indicator-Trading-Signal-Strategy -> `fmz_446549_ema12_26_cross_adx_atr_hist_supertrend_exit_reversal`

- FMZ source id: 446549 (lineage).
- Source: https://www.fmz.com/strategy/446549 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 15:41:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with trend, volatility and MACD filters, SuperTrend exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 70 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [15.0, 25.0] x `factor` [3.0, 2.0]: **4 trials**; the EMAs, the ATR filter and the SuperTrend length fixed.

## Ambiguities resolved

- Backtest window dropped; script's ADX. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
