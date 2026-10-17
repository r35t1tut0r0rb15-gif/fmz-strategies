# #489154 多重均线交叉动量风险比优化策略-Multi-EMA-Crossover-Momentum-Strategy-with-Risk-Reward-Optimization -> `fmz_489154_golden_death_cross_bracket`

- FMZ source id: 489154 (lineage).
- Source: https://www.fmz.com/strategy/489154 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 11:19:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `rr` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 50 / 200 fixed.

## Ambiguities resolved

- The bracket is placed on the signal bar; re-based on the fill (house rule).
- REVERSAL INTENDED. FREQ = "2h"; stops on 2-hour bars: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
