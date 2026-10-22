# #473147 EMA Crossover Strategy with Stop Loss and Take Profit Optimization System -> `fmz_473147_ema5_15_cross_prev_avg_pct_bracket_reversal`

- FMZ source id: 473147 (lineage).
- Source: https://www.fmz.com/strategy/473147 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:15:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | EMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [15, 21] x `tp_pct` [0.03, 0.06]: **8 trials**; the 1.5 % stop fixed.

## Ambiguities resolved

- Bracket base is the replaced position's average price (na from flat), as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
