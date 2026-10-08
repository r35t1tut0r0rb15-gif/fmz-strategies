# #426477 Multi Indicator Convergence Trading Strategy -> `fmz_426477_td_macd_rsi_bb`

- Source: https://www.fmz.com/strategy/426477 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-12 14:27:41). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distance -> ATR(14) multiple at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426477` (Jaccard >= 0.80) with #430127 (DUPLICATE); best Jaccard 0.880 with #430127. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_diff` [-7, -14] x `tp_atr` [0.25, 1.0, 2.0]: **6 trials**, defaults -7 / 0.25 (the source's -7; 0.25 is the smallest step, the 500-tick target being a small fraction of a daily ATR).

## Ambiguities resolved

- Criterion 2 (ADAPT): 500-tick target -> tp_atr x ATR(14) at the signal bar; the stop is off by default (no sl_stop).
- Entries only from flat; simulate() mirrors the engine's target from the fill bar on.
- Pine population stdev; TDUp / TDDn only plot.
- Daily bars are broker days; target on daily bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`coarse_bar_stop`
