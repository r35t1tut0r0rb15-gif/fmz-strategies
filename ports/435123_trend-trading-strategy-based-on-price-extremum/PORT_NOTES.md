# #435123 Trend Trading Strategy Based on Price Extremum -> `fmz_435123_fractal_chaos_bands`

- FMZ source id: 435123 (lineage).
- Source: https://www.fmz.com/strategy/435123 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 14:36:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427136. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pattern` [1, 2, 3]: **3 trials**.

## Ambiguities resolved

- Fractals confirmed pattern bars later. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
