# #468319 EMA-MACD-动量跟踪策略EMA-MACD-Momentum-Tracking-Strategy -> `fmz_468319_ema9_21_and_macd_cross_atr_bracket_reversal`

- FMZ source id: 468319 (lineage).
- Source: https://www.fmz.com/strategy/468319 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:31:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR levels from the fill |
| 2 | PASS | EMA and MACD crossings together with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 34] x `atr_mult` [1.5, 3.0]: **8 trials**; the MACD lengths fixed.

## Ambiguities resolved

- ATR of the bar before the fill; per-bar ATR movement pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
