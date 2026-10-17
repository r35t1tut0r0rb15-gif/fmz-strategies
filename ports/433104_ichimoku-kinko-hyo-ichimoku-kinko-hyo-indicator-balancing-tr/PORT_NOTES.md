# #433104 Ichimoku-Kinko-Hyo趋势跟踪策略Ichimoku-Kinko-Hyo-indicator-Balancing-Trend-Strategy -> `fmz_433104_ichimoku_rsi_body_filter`

- FMZ source id: 433104 (lineage).
- Source: https://www.fmz.com/strategy/433104 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 14:38:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines, momentum sign, RSI and a percent body filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_target` [0.2, 0.1] x `offset` [30, 26]: **4 trials**; Ichimoku 22 / 60 / 120, vol length 2 and RSI 14 fixed.

## Ambiguities resolved

- Bearish RSI test on rs as written. REVERSAL INTENDED. FREQ = "3min" (the title's 3h is not used).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
