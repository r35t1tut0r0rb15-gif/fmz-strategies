# #437694 Multi indicator Collision Reversal Strategy -> `fmz_437694_reversal123_n_bars_up_combo`

- FMZ source id: 437694 (lineage).
- Source: https://www.fmz.com/strategy/437694 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 18:02:12). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and candle counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430768. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `n_length` [4, 3]: **4 trials**; K smoothing 1, D 3 and level 50 fixed; reverse off.

## Ambiguities resolved

- N-bars-up state never resets and is never short (long or flat only), as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
