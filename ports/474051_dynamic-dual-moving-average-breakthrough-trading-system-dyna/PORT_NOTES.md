# #474051 Dynamic Dual Moving Average Breakthrough Trading System Dynamic Dual Moving Average Breakthrough Trading System -> `fmz_474051_ema9_21_cross_avg_bracket_5_10_reversal_inputs`

- FMZ source id: 474051 (lineage).
- Source: https://www.fmz.com/strategy/474051 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:22:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | EMA crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND473396. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.05, 0.03] x `tp_pct` [0.10, 0.06]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Same rules as #473396. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
