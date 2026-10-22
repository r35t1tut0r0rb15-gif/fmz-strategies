# #451705 Ichimoku Cloud and Moving Average Strategy -> `fmz_451705_sma55_reclaim_cloud_sma200_reversal`

- FMZ source id: 451705 (lineage).
- Source: https://www.fmz.com/strategy/451705 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:55:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA reclaims filtered by the cloud and the SMA 200 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ma` [55, 20] x `long_ma` [200, 100]: **4 trials**; the Ichimoku lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
