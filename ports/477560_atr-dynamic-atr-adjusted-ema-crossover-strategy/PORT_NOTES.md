# #477560 动态ATR调整的指数均线交叉策略-Dynamic-ATR-Adjusted-EMA-Crossover-Strategy -> `fmz_477560_ema9_21_cross_atr_bracket_reversal`

- FMZ source id: 477560 (lineage).
- Source: https://www.fmz.com/strategy/477560 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:56:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [2.0, 3.0] x `sl_mult` [1.0, 1.5]: **4 trials**; EMA 9 / 21, ATR 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
