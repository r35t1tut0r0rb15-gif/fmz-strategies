# #443231 突破EMA滑动止损三角策略Elevated-Touch-Short-Triangle-Strategy -> `fmz_443231_ema5_first_touch_prev_bar_bracket_short`

- FMZ source id: 443231 (lineage).
- Source: https://www.fmz.com/strategy/443231 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-01 11:02:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from bar data |
| 2 | PASS | First EMA touch from above |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [5, 10] x `rr` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Levels from the previous bar; wrong-side levels give no order. Short only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
