# #473319 KNN自适应参数化趋势跟踪策略-KNN-Based-Adaptive-Parametric-Trend-Following-Strategy -> `fmz_473319_knn_self_window_recursive_change_sma50_reversal`

- FMZ source id: 473319 (lineage).
- Source: https://www.fmz.com/strategy/473319 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-11-29 10:54:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Recursive change average with an SMA filter, as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash size and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k` [5, 3] x `ma_length` [50, 100]: **4 trials**; the window 20 (only its start bar reaches the orders).

## Ambiguities resolved

- The KNN search collapses as written (every neighbour index 0). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
