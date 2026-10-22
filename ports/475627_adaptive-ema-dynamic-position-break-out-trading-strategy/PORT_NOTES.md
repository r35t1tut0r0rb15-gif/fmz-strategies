# #475627 Adaptive EMA Dynamic Position Break out Trading Strategy -> `fmz_475627_ema25_100_cross_last_red_low_stop_3r_long`

- FMZ source id: 475627 (lineage).
- Source: https://www.fmz.com/strategy/475627 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 16:33:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA cross-ups with a swing stop and 3 R target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [25, 10] x `slow` [100, 50]: **4 trials**; 3 R.

## Ambiguities resolved

- Break-even and repeat-cross re-sends not followed. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
