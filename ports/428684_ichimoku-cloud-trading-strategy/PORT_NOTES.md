# #428684 Ichimoku Cloud Trading Strategy -> `fmz_428684_ichimoku_cloud_position`

- FMZ source id: 428684 (lineage).
- Source: https://www.fmz.com/strategy/428684 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 12:24:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the cloud is from 26 bars ago. |
| 2 | PASS | Channel lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 7] x `base` [26, 22]: **4 trials**; defaults 9 / 26 (the source's); span B 52 and the 26-bar lag fixed.

## Ambiguities resolved

- The [26] lag is in the conditions; the displacement input only moves plots. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
