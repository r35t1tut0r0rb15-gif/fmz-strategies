# #482684 多重时间框架动态趋势跟踪策略结合EMA与ADX指标-Multi-Timeframe-Dynamic-Trend-Following-Strategy-with-EMA-and-ADX-Integration -> `fmz_482684_ema50_200_cross_adx25_rsi_pct3_bracket_rsi_exit_reversal`

- FMZ source id: 482684 (lineage).
- Source: https://www.fmz.com/strategy/482684 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with ADX and RSI filters and RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity stored, not ported; commission and slippage not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25, 20] x `bracket_frac` [0.03, 0.06]: **4 trials**; EMA 50 / 200, DMI 14, RSI 14, 70 / 30.

## Ambiguities resolved

- A repeat crossing's re-sent bracket is pending and its bar's RSI close is dropped.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
