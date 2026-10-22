# #481349 跨周期动量均线交叉策略结合RSI与ATR动态止损-Cross-Period-Momentum-EMA-Strategy-with-RSI-and-Dynamic-ATR-Stop-Loss -> `fmz_481349_ema9_21_cross_rsi_filter_atr_bracket_reversal`

- FMZ source id: 481349 (lineage).
- Source: https://www.fmz.com/strategy/481349 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:34:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `tp_factor` [2.0, 4.0]: **4 trials**; EMA 9 / 21, RSI 14, ATR 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
