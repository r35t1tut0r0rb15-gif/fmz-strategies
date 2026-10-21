# #437783 Visual Comparison between Strategy and Buy Hold Returns -> `fmz_437783_sma50_200_cross_vs_buyhold`

- FMZ source id: 437783 (lineage).
- Source: https://www.fmz.com/strategy/437783 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 15:27:26). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- Always-true comparison window; display-only buy-and-hold panel. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
