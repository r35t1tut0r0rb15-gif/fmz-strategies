# #432358 Ichimoku-Kinko-Hyo交易策略Ichimoku-Kinko-Hyo-Trading-Strategy -> `fmz_432358_ichimoku_cloud_break`

- FMZ source id: 432358 (lineage).
- Source: https://www.fmz.com/strategy/432358 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 17:31:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 7] x `span_b` [52, 44]: **4 trials**; base 26 and displacement 26 fixed.

## Ambiguities resolved

- Spans read 26 / 27 bars back. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
