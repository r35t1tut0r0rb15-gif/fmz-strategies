# #433579 Commodity Momentum Index Strategy -> `fmz_433579_csi_vs_average`

- FMZ source id: 433579 (lineage).
- Source: https://www.fmz.com/strategy/433579 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 16:27:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR x ADXR line against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point value / margin / commission constants only scale the line. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
