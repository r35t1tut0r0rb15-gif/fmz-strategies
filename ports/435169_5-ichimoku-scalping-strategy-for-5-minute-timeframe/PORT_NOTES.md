# #435169 基于一目均衡表的5分钟快速突破策略Ichimoku-Scalping-Strategy-for-5-Minute-Timeframe -> `fmz_435169_tk_cross_cloud_side`

- FMZ source id: 435169 (lineage).
- Source: https://www.fmz.com/strategy/435169 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 18:12:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | Ichimoku crosses and spans |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 20] x `base` [26, 52]: **4 trials**; Span B 52 fixed.

## Ambiguities resolved

- Bracket armed only by repeated signals: not ported (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`
