# #435139 Ichimoku-Early-Cloud-Trend-Following-Strategy-一云双提前知机会均线趋势跟踪策略 -> `fmz_435139_ichimoku_chikou_free_cloud`

- FMZ source id: 435139 (lineage).
- Source: https://www.fmz.com/strategy/435139 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 16:11:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku spans |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 99 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`disp` [26, 13] x `long_only` [False, True]: **4 trials**; Tenkan 9, Kijun 26, Senkou B 52 fixed.

## Ambiguities resolved

- Displaced spans read from past bars; the off-by-default stop not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
