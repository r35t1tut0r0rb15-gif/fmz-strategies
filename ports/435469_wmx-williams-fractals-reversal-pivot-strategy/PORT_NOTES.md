# #435469 WMX Williams Fractals Reversal Pivot Strategy -> `fmz_435469_fractal_level_cross_on_close`

- FMZ source id: 435469 (lineage).
- Source: https://www.fmz.com/strategy/435469 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 10:37:01). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [2, 3] x `occurrence` [3, 1]: **4 trials**.

## Ambiguities resolved

- Fractals on closes; valuewhen on state changes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "fractal_breakout"`.

## Marks

`none`
