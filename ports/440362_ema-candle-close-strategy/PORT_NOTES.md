# #440362 EMA Candle Close Strategy -> `fmz_440362_close_vs_hma20`

- FMZ source id: 440362 (lineage).
- Source: https://www.fmz.com/strategy/440362 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 16:02:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against the HMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len2` [20, 50]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
