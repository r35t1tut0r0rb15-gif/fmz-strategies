# #435724 基于CCI指标的长线交易策略CCI-Long-Only-Strategy -> `fmz_435724_cci_alternating_latch_long`

- FMZ source id: 435724 (lineage).
- Source: https://www.fmz.com/strategy/435724 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 12:32:07). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_period` [14, 20, 28]: **3 trials**; levels +-100 fixed.

## Ambiguities resolved

- Alternating latch as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cci_oscillator"`.

## Marks

`none`
