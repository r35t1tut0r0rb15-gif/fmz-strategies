# #446457 SMA均线交叉策略SMA-Moving-Average-Crossover-Strategy -> `fmz_446457_sma30_100_cross_long`

- FMZ source id: 446457 (lineage).
- Source: https://www.fmz.com/strategy/446457 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 17:50:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [30, 50] x `slow` [100, 200]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
