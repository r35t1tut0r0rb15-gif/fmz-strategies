# #433123 动量分析式Ichimoku云雾闪电交易策略Momentum-Analysis-Ichimoku-Cloud-Fog-Lightning-Trading-Strategy -> `fmz_433123_ichimoku_scalp_bracket`

- FMZ source id: 433123 (lineage).
- Source: https://www.fmz.com/strategy/433123 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 15:49:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Ichimoku crosses and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.015, 0.03] x `tp_pct` [0.01, 0.02]: **4 trials**; Ichimoku 9 / 26 / 52 / 26 fixed.

## Ambiguities resolved

- One-bar shorts (the long-side exit levels on shorts, as written). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
