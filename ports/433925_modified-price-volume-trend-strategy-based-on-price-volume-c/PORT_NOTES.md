# #433925 Modified Price Volume Trend Strategy Based on Price Volume Changes -> `fmz_433925_modified_price_volume_trend_sma23_state_reversal`

- FMZ source id: 433925 (lineage).
- Source: https://www.fmz.com/strategy/433925 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-01 14:56:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-volume trend against its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [23, 50]: **2 trials**; level 0, scale 1.

## Ambiguities resolved

- Volume = broker tick volume (PVT). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
