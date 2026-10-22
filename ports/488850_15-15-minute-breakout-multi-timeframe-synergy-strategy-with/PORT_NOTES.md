# #488850 15分钟突破多周期协同策略基于风险收益比优化模型15-Minute-Breakout-Multi-Timeframe-Synergy-Strategy-with-Risk-Reward-Optimization-Model -> `fmz_488850_prev_bar_breakout_prev_extreme_stop_3r_reversal`

- FMZ source id: 488850 (lineage).
- Source: https://www.fmz.com/strategy/488850 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 17:32:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous-bar bracket as fractions of the fill |
| 2 | PASS | Previous-bar breakouts with a 3 R bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 100000, 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [3.0, 1.5]: **2 trials**; previous-bar levels.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "range_breakout"`.

## Marks

`trailing_stop_pending`
