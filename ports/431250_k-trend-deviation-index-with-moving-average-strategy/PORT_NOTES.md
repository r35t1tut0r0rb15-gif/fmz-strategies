# #431250 趋势偏离指标K线结合移动平均线波浪策略Trend-Deviation-Index-with-Moving-Average-Strategy -> `fmz_431250_hull_tsi_open`

- FMZ source id: 431250 (lineage).
- Source: https://www.fmz.com/strategy/431250 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 14:46:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A ratio of smoothed price changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 25] x `signal` [7, 14]: **4 trials**; long = short length.

## Ambiguities resolved

- Open as the source, as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
