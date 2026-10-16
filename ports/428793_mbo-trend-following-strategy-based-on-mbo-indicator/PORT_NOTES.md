# #428793 基于MBO指标的趋势跟随策略Trend-Following-Strategy-Based-on-MBO-Indicator -> `fmz_428793_tfs_mbo`

- FMZ source id: 428793 (lineage).
- Source: https://www.fmz.com/strategy/428793 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-09 15:22:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A comparison of two series in the same units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [25, 12] x `length` [18, 9]: **4 trials**; slow 200 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
