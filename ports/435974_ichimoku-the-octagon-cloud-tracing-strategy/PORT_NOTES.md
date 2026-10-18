# #435974 八角云霄-Ichimoku-趋势追踪策略The-Octagon-Cloud-Tracing-Strategy -> `fmz_435974_cloud_tenkan_trades`

- FMZ source id: 435974 (lineage).
- Source: https://www.fmz.com/strategy/435974 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-20 15:08:22). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud and Tenkan rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [10, 9] x `kijun` [30, 26]: **4 trials**; span B 60 and displacement 30 fixed.

## Ambiguities resolved

- Plain open / close; cloud 29 bars back; orders in call order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
