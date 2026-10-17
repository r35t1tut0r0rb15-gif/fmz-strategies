# #482849 自适应均线交叉动态头寸风险管理策略-Adaptive-EMA-Crossover-Dynamic-Position-Risk-Management-Strategy -> `fmz_482849_ema21_55_cross_two_bar_stop_2r`

- FMZ source id: 482849 (lineage).
- Source: https://www.fmz.com/strategy/482849 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:36:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar. |
| 2 | PASS | Moving averages and the bar extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 3.0] x `stop_bars` [2, 5]: **4 trials**; defaults 2 / 2 (the source's); EMA 21 / 55 fixed.

## Ambiguities resolved

- The 2-bar extreme stop and the 2 R target become fractions of the signal close by side, re-based on the fill; a
  signal whose stop is not beyond the close emits no entry (as #490798). Crosses alternate: no re-placement.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
