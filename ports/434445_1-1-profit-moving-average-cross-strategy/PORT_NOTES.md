# #434445 均线黄金交叉1止盈策略1-Profit-Moving-Average-Cross-Strategy -> `fmz_434445_sma_cross_tick_target`

- FMZ source id: 434445 (lineage).
- Source: https://www.fmz.com/strategy/434445 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 13:53:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long target fixed at entry |
| 2 | PASS | Average crosses and a fill-relative target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 60]: **4 trials**; the as-written 0.01-tick target fixed.

## Ambiguities resolved

- Profit in ticks: 0.01 tick as written (tp_stop 1e-6; the 1 % version owed). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "3D" (blocks of 3 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
