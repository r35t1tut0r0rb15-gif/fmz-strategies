# #477554 Momentum Trend Ichimoku Cloud Trading Strategy -> `fmz_477554_ichimoku_tenkan_kijun_cross_reversal`

- FMZ source id: 477554 (lineage).
- Source: https://www.fmz.com/strategy/477554 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:49:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku Tenkan / Kijun crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `base` [26, 60]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
