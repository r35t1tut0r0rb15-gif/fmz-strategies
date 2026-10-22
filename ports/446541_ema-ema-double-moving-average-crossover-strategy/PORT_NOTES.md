# #446541 EMA双均线交叉策略-EMA-Double-Moving-Average-Crossover-Strategy -> `fmz_446541_ema20_50_cross_gangmei_reversal`

- FMZ source id: 446541 (lineage).
- Source: https://www.fmz.com/strategy/446541 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 15:06:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Same rules as #446460. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
