# #430887 Combo Strategy of 123 Reversal and Fractal Chaos Oscillator -> `fmz_430887_combo_123_fractal_chaos`

- FMZ source id: 430887 (lineage).
- Source: https://www.fmz.com/strategy/430887 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 16:43:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A stochastic and fractal states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430887. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 30] x `pattern` [1, 2]: **4 trials**; K 1, D 3 and level 50 fixed.

## Ambiguities resolved

- Both fractals changing on one bar: up wins, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
