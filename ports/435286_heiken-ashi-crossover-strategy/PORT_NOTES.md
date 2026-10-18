# #435286 Heiken Ashi Crossover Strategy -> `fmz_435286_heikin_ashi_colour`

- FMZ source id: 435286 (lineage).
- Source: https://www.fmz.com/strategy/435286 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-13 17:46:10). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

no searched parameter: **1 trial**.

## Ambiguities resolved

- Colour changes only; no parameter. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
