# #482901 均线动态趋势跟踪与RSI-ADX复合指标交易策略-Dynamic-Moving-Average-Trend-Following-Strategy-with-RSI-ADX-Composite-Indicators -> `fmz_482901_sma200_cross_confirm2_rsi_adx_atr_pct_bracket_long`

- FMZ source id: 482901 (lineage).
- Source: https://www.fmz.com/strategy/482901 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:27:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR / percent bracket as fractions of the fill |
| 2 | PASS | Confirmed SMA 200 crossings with RSI / ADX filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [200, 100] x `atr_mult` [1.5, 2.5]: **4 trials**; RSI 14 / 40 / 60, ADX 14 over 20, target 2 %.

## Ambiguities resolved

- The flat gate is followed in a loop with the bracket on bar highs / lows. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
