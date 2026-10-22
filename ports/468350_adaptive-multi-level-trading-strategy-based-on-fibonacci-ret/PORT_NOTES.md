# #468350 Adaptive Multi Level Trading Strategy Based on Fibonacci Retracement -> `fmz_468350_range100_fib618_382_cross_pip_bracket_reversal`

- FMZ source id: 468350 (lineage).
- Source: https://www.fmz.com/strategy/468350 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 17:21:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the pip bracket as fractions of the fill |
| 2 | PASS | Retracement-line crossings with a pip bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [100, 50] x `tp_frac` [0.00119, 0.01] x `sl_frac` [0.000476, 0.005]: **8 trials**; the levels fixed.

## Ambiguities resolved

- Pips as fractions of 42000. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop`
