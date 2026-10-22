# #440853 DMI Balance Buy Sell Strategy -> `fmz_440853_dmi_double_cross_long`

- FMZ source id: 440853 (lineage).
- Source: https://www.fmz.com/strategy/440853 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 17:07:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | DMI crossings |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `adx_smoothing` [14, 7]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`bar_size_pending`
