# #433560 Multi-SMA均线交叉策略Multi-SMA-Moving-Average-Crossover-Strategy -> `fmz_433560_five_sma_mean_trend`

- FMZ source id: 433560 (lineage).
- Source: https://www.fmz.com/strategy/433560 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 15:08:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The close against an average and its slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`scale` [1.0, 2.0]: **2 trials**; scale multiplies all five lengths (8 / 21 / 50 / 100 / 200 as written).

## Ambiguities resolved

- Level entries. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
