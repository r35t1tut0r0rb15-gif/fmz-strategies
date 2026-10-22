# #442964 Ichimoku Cloud Trend Following Strategy -> `fmz_442964_ichimoku_tk_cross_cloud_conv_exit`

- FMZ source id: 442964 (lineage).
- Source: https://www.fmz.com/strategy/442964 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:41:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TK crosses with the cloud |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `span_b` [52, 120]: **4 trials**; the base line and displacement fixed.

## Ambiguities resolved

- Cloud as plotted at the current bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
