# #473252 Triple EMA Crossover Trading Strategy with Dynamic Stop Loss and Take Profit -> `fmz_473252_ema9_15_cross_ema50_filter_tick_bracket_long`

- FMZ source id: 473252 (lineage).
- Source: https://www.fmz.com/strategy/473252 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:54:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | EMA crossings with a trend filter and a tick bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.01, 1.0] x `tp_atr` [0.02, 2.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Ticks as ATR multiples (1D ~1000). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
