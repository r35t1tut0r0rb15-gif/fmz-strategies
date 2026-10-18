# #435895 Ichimoku均线交叉策略Ichimoku-Moving-Average-Crossover-Strategy -> `fmz_435895_kijun_side_pullback_candle`

- FMZ source id: 435895 (lineage).
- Source: https://www.fmz.com/strategy/435895 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 15:40:53). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel midpoint and candle filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base` [26, 52] x `use_body_filter` [True, False]: **4 trials**; the colour filter stays on.

## Ambiguities resolved

- Pullback candle colour as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
