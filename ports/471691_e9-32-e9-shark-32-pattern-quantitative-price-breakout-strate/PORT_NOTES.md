# #471691 E9鲨鱼32形态量化价格突破策略-E9-Shark-32-Pattern-Quantitative-Price-Breakout-Strategy -> `fmz_471691_shark32_inside_pattern_breakout_range_target_reversal`

- FMZ source id: 471691 (lineage).
- Source: https://www.fmz.com/strategy/471691 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:51:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the pattern target as a fraction of the fill |
| 2 | PASS | Inside-bar pattern breakouts with a range target; per-bar stop described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target_mult` [1.0, 0.5]: **2 trials**; the per-bar stop pending.

## Ambiguities resolved

- Target from the signal bar's pattern; per-bar stop and later pattern updates pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
