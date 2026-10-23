# #474711 Volume Weighted Dual Trend Detection System -> `fmz_474711_volume_weighted_body_delta_cross_reversal`

- FMZ source id: 474711 (lineage).
- Source: https://www.fmz.com/strategy/474711 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:41:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-weighted candle-body delta crossings of its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`delta_len` [5, 10] x `ma_len` [5, 10]: **4 trials**.

## Ambiguities resolved

- Inverted labels ported as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_delta"`.

## Marks

`none`
