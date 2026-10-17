# #483042 市云转向指标改良型多空交叉交易策略-Enhanced-Ichimoku-Cloud-Trading-Strategy-with-Dynamic-Crossover-Signals -> `fmz_483042_tenkan_kijun_cross_long`

- FMZ source id: 483042 (lineage).
- Source: https://www.fmz.com/strategy/483042 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:41:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Donchian mid lines. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 7] x `base` [26, 22]: **4 trials**; defaults 9 / 26 (the source's).

## Ambiguities resolved

- The spans and the lagging line are only plotted. Long only: opposite entries cannot occur. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
