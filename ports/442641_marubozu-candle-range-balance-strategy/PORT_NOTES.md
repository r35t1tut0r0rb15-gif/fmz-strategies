# #442641 Marubozu Candle Range Balance Strategy -> `fmz_442641_marubozu_inverted_direction_reversal`

- FMZ source id: 442641 (lineage).
- Source: https://www.fmz.com/strategy/442641 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-23 14:23:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Marubozu candle pattern (directions as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_len` [14, 30] x `shadow_pct` [5.0, 10.0]: **4 trials**.

## Ambiguities resolved

- Directions inverted as written; closes by id. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
