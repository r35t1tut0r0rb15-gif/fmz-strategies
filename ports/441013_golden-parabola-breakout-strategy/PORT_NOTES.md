# #441013 Golden Parabola Breakout Strategy -> `fmz_441013_dominant_candle_5ma_band_reversal`

- FMZ source id: 441013 (lineage).
- Source: https://www.fmz.com/strategy/441013 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 18:07:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle pattern and band tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG441013. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
