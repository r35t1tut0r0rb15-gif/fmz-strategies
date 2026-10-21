# #438972 基于Ichimoku-Kinko-Hyo指标的突破策略Ichimoku-Kinko-Hyo-Breakout-Strategy -> `fmz_438972_ichimoku_cloud_breakout_long`

- FMZ source id: 438972 (lineage).
- Source: https://www.fmz.com/strategy/438972 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-16 17:12:49). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines and displaced cloud |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ts_bars` [7, 9] x `ks_bars` [14, 26]: **4 trials**; Senkou B 28 and the 14 offsets fixed.

## Ambiguities resolved

- Shorts off: the bearish setup closes. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
