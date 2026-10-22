# #478737 Multi Timeframe Trading Strategy Combining Harmonic Patterns and Williams R -> `fmz_478737_pivot5_williams_r_extreme_bracket_reversal`

- FMZ source id: 478737 (lineage).
- Source: https://www.fmz.com/strategy/478737 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:19:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Confirmed pivots with Williams %R extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pattern_length` [5, 10] x `rr_mult` [0.618, 0.01]: **4 trials**; WPR 14 / -20 / -80, buffer 0.5 %.

## Ambiguities resolved

- The 0.618 target multiplier is a 61.8 % price move, as written. Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`trailing_stop_pending`
