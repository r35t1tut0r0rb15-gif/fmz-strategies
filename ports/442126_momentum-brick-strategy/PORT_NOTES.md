# #442126 Momentum Brick Strategy -> `fmz_442126_flex_renko_brick_turn_reversal`

- FMZ source id: 442126 (lineage).
- Source: https://www.fmz.com/strategy/442126 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 15:32:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Renko brick direction changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [14, 7]: **2 trials**.

## Ambiguities resolved

- Brick line from zero, one brick per bar, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "renko_bricks"`.

## Marks

`none`
