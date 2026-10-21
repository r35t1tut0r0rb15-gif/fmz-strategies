# #438052 Monthly Performance PnL Calendar Strategy -> `fmz_438052_close_vs_bar20_extremes`

- FMZ source id: 438052 (lineage).
- Source: https://www.fmz.com/strategy/438052 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 16:16:58). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Comparisons with a past bar's extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 10, 40, 55]: **4 trials**.

## Ambiguities resolved

- Single past bar compared (high[20] / low[20]); table display only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
