# #440558 Recursive Momentum Trading Strategy -> `fmz_440558_recursive_band_touch_reversal`

- FMZ source id: 440558 (lineage).
- Source: https://www.fmz.com/strategy/440558 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 16:56:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Recursive bands of past closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [260, 100] x `lookback` [3, 5]: **4 trials**.

## Ambiguities resolved

- Classic method; middle-line take-profit commented out. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_reversal"`.

## Marks

`none`
