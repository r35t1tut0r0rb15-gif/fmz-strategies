# #476277 Multi Period Fractal Breakout Order Block Adaptive Trading Strategy -> `fmz_476277_fractal2_level_break_once_reversal`

- FMZ source id: 476277 (lineage).
- Source: https://www.fmz.com/strategy/476277 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:49:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal level breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [2, 3, 5]: **3 trials**; break type Wick+Body.

## Ambiguities resolved

- Breaks against the level from the previous bar; non-strict fractals, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
