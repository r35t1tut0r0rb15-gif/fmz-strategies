# #474052 动态止损倍数多周期RSI趋势跟踪策略-Dynamic-Stop-Loss-Multi-Period-RSI-Trend-Following-Strategy -> `fmz_474052_ema9_21_cross_rsi_atr_bracket_2_4_reversal`

- FMZ source id: 474052 (lineage).
- Source: https://www.fmz.com/strategy/474052 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:25:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Size from a typed balance stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [4, 2] x `sl_mult` [2, 1]: **4 trials**; the EMA / RSI / ATR lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
