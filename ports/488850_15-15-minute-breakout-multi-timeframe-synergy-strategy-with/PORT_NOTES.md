# #488850 15分钟突破多周期协同策略基于风险收益比优化模型15-Minute-Breakout-Multi-Timeframe-Synergy-Strategy-with-Risk-Reward-Optimization-Model -> `fmz_488850_previous_bar_breakout_3r`

- FMZ source id: 488850 (lineage).
- Source: https://www.fmz.com/strategy/488850 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 17:32:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Bar levels and a reward ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [3.0, 1.5]: **2 trials**; 3 is the source's.

## Re-placed bracket (rule 2, mark `trailing_stop_pending`)

Each later signal bar while in the trade re-issues the exit at its own previous-bar level and 3 R target (the entry
being ignored). The port keeps the entry's bracket.

## Ambiguities resolved

- The "15" security on the 15-minute chart is the bar itself: the levels are the previous bar's high and low.
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`trailing_stop_pending`
