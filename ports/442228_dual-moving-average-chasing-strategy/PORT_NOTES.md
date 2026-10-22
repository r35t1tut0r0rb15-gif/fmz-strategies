# #442228 Dual Moving Average Chasing Strategy -> `fmz_442228_heikin_ashi_flat_flip_reversal`

- FMZ source id: 442228 (lineage).
- Source: https://www.fmz.com/strategy/442228 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 14:11:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Heikin-Ashi crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- Same-timeframe Heikin Ashi. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
