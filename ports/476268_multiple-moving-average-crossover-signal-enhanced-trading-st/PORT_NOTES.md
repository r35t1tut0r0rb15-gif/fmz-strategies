# #476268 Multiple Moving Average Crossover Signal Enhanced Trading Strategy -> `fmz_476268_sma20_50_cross_sma200_side_long`

- FMZ source id: 476268 (lineage).
- Source: https://www.fmz.com/strategy/476268 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:34:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an SMA 200 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; SMA 200 filter.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
