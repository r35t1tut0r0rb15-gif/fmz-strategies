# #482906 Composite Trend Moving Average Reversal Trading Strategy -> `fmz_482906_composite_ema25_pullback_reaction_0_5pct_reversal`

- FMZ source id: 482906 (lineage).
- Source: https://www.fmz.com/strategy/482906 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:23:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA pullback reactions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_a` [20, 10] x `reaction_perc` [0.5, 1.0]: **4 trials**; period B 30, composite average, EMA.

## Ambiguities resolved

- Menu defaults EMA / Average. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
