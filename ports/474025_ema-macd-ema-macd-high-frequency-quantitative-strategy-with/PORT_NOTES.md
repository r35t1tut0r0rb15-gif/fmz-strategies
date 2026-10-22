# #474025 EMA-MACD高频量化策略与智能风控系统-EMA-MACD-High-Frequency-Quantitative-Strategy-with-Smart-Risk-Management -> `fmz_474025_ema9_21_cross_macd6_13_4_atr_bracket_reversal`

- FMZ source id: 474025 (lineage).
- Source: https://www.fmz.com/strategy/474025 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 14:54:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a MACD filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size from equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and multiples are constants).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
