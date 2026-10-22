# #473265 多均线趋势跟踪与ATR动态目标策略-Multi-EMA-Trend-Following-Strategy-with-Dynamic-ATR-Targets -> `fmz_473265_ema_stack_pullback_21_50_atr_bracket_long`

- FMZ source id: 473265 (lineage).
- Source: https://www.fmz.com/strategy/473265 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:11:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at entry |
| 2 | PASS | EMA-stack pullbacks with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 3.0] x `tp_atr` [3.5, 7.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
