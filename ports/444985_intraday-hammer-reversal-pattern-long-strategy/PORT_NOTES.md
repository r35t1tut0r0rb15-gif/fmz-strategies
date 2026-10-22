# #444985 Intraday Hammer Reversal Pattern Long Strategy -> `fmz_444985_red_hammer_green_follow_long_stop_low`

- FMZ source id: 444985 (lineage).
- Source: https://www.fmz.com/strategy/444985 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 17:13:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop and target fixed on the signal bar |
| 2 | PASS | Hammer and follow-up candle pattern |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 50000 / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_frac` [0.3, 0.5] x `target_mult` [1.5, 1.1]: **4 trials**; the wick ratio and the upper-wick tolerance fixed.

## Ambiguities resolved

- Levels from the signal bar; repeat-signal level moves not followed (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
