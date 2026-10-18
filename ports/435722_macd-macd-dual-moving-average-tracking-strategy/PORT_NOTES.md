# #435722 基于MACD指标的双均线交易策略MACD-Dual-Moving-Average-Tracking-Strategy -> `fmz_435722_fast_macd_cross_long`

- FMZ source id: 435722 (lineage).
- Source: https://www.fmz.com/strategy/435722 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-18 12:25:13). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | The previous-low exit switch has no effect (local re-declaration) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash order size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `slow` [8, 13]: **4 trials**; signal SMA 3 fixed.

## Ambiguities resolved

- Local re-declaration: exit on the red cross only. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
