# #473936 Bollinger Bands High Frequency Quantitative Strategy Combined with High Low Breakout System -> `fmz_473936_bb20_outside_bar_break_prev_range_bracket_reversal`

- FMZ source id: 473936 (lineage).
- Source: https://www.fmz.com/strategy/473936 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:15:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Band-outside bar breaks with a 1 : 1 bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`
