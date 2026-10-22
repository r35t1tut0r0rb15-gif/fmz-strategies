# #476260 Multi EMA Dynamic Trend Capture Quantitative Trading Strategy -> `fmz_476260_ema9_21_cross_ema200_side_reversal`

- FMZ source id: 476260 (lineage).
- Source: https://www.fmz.com/strategy/476260 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 14:59:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an EMA 200 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `filter` [200, 100]: **4 trials**; slow EMA 21.

## Ambiguities resolved

- Trade mode Both. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
