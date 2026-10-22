# #471694 多周期RSI动量与三重EMA趋势跟踪复合策略-Multi-Period-RSI-Momentum-and-Triple-EMA-Trend-Following-Composite-Strategy -> `fmz_471694_one_bar_rsi_up_bar_short_down_bar_cover`

- FMZ source id: 471694 (lineage).
- Source: https://www.fmz.com/strategy/471694 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:07:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the break-even level as a fraction of the fill |
| 2 | PASS | One-bar swing shorts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the one-bar RSI makes every level a sign test).

## Ambiguities resolved

- The long branch never fires (as written). Short only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
