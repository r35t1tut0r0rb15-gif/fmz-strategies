# #441097 5 Day Moving Average Channel Breakout Strategy Combined With Mileage Concept -> `fmz_441097_mileage_candle_5ma_band_long`

- FMZ source id: 441097 (lineage).
- Source: https://www.fmz.com/strategy/441097 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 15:16:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle pattern and band tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10]: **2 trials**.

## Ambiguities resolved

- The short side cannot trigger as written: long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
