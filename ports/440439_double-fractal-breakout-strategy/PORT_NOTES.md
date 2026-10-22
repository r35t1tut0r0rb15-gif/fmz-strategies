# #440439 Double Fractal Breakout Strategy -> `fmz_440439_second_fractal_breakout`

- FMZ source id: 440439 (lineage).
- Source: https://www.fmz.com/strategy/440439 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 15:53:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fractals confirmed from past bars |
| 2 | PASS | Fractal levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`occurrence` [1, 0]: **2 trials**; 1 is the script's second-latest fractal, 0 the latest.

## Ambiguities resolved

- Second-latest fractal as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "fractal_breakout"`.

## Marks

`none`
