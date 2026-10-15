# #427136 Fractal Chaos Oscillator Trading Strategy -> `fmz_427136_fractal_chaos_oscillator`

- FMZ source id: 427136 (lineage).
- Source: https://www.fmz.com/strategy/427136 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 15:10:09). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.
- Near-duplicate group: **ND427136** (with #435123, Jaccard 0.743); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders on fractals confirmed p bars after the peak. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427136. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pattern` [1, 2, 3]: **3 trials**; default 1 (the source's). The only parameter besides "reverse" (off).

## Ambiguities resolved

- A first fractal (previous value na) and a new fractal at the same level are not changes (Pine na / equality semantics, as written).
- Up-fractal change wins over a down-fractal change on the same bar (script order).
- Always in the market (REVERSAL INTENDED). FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
