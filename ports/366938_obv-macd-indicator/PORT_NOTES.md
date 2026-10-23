# #366938 OBV MACD Indicator -> `fmz_366938_obv_shadow_dema_macd_running_extreme_pivot_reversal`

- FMZ source id: 366938 (lineage).
- Source: https://www.fmz.com/strategy/366938 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 18:46:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OBV-shadow MACD running-extreme pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [9, 21] x `xbars` [50, 100]: **4 trials**; slow 26, windows 28 / 14.

## Ambiguities resolved

- Long on top pivots / short on bottom pivots, as written; the close-vs-line reset kept. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
