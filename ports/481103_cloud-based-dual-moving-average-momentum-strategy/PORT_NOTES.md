# #481103 Cloud Based Dual Moving Average Momentum Strategy -> `fmz_481103_ichimoku_cloud_tk_state_2d_reversal`

- FMZ source id: 481103 (lineage).
- Source: https://www.fmz.com/strategy/481103 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 15:10:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku cloud and Tenkan / Kijun states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `kijun` [26, 60]: **4 trials**; span B 52.

## Ambiguities resolved

- Spans read undisplaced. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
