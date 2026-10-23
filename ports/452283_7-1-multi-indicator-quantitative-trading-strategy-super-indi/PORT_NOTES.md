# #452283 多指标量化交易策略-7合1超级指标策略-Multi-Indicator-Quantitative-Trading-Strategy-Super-Indicator-7-in-1-Strategy -> `fmz_452283_seven_in_one_extremes_count_tight_bracket_3h_reversal`

- FMZ source id: 452283 (lineage).
- Source: https://www.fmz.com/strategy/452283 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-23 18:20:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tight bracket at the signal close as fractions of the fill |
| 2 | PASS | Oversold / overbought confluence counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): cash 10000 per order, capital 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.0014, 0.005] x `sl_pct` [0.0025, 0.01]: **4 trials**; BB 20 x 2, RSI 14, stochastic 14.

## Ambiguities resolved

- Volume test always true; the other side's pending exit is not followed. Volume not used. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
