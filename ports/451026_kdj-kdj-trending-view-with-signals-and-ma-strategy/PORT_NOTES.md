# #451026 KDJ趋势跟踪与信号移动平均策略-KDJ-Trending-View-with-Signals-and-MA-Strategy -> `fmz_451026_kdj_j_extreme_sma20_cross_reversal`

- FMZ source id: 451026 (lineage).
- Source: https://www.fmz.com/strategy/451026 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 11:46:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | KDJ J extremes with SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kdj_len` [9, 14] x `ma_len` [20, 50]: **4 trials**; the signal 3 and the levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
