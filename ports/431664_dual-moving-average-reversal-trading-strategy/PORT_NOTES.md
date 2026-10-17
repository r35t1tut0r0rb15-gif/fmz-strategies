# #431664 Dual Moving Average Reversal Trading Strategy -> `fmz_431664_two_candle_colour_fade`

- FMZ source id: 431664 (lineage).
- Source: https://www.fmz.com/strategy/431664 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-10 11:18:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked time exit |
| 2 | PASS | Candle colours and a holding time |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_hours` [280, 72] x `bars` [2, 3]: **4 trials** (bars = candles of one colour in a row).

## Ambiguities resolved

- Time exit from the fill, close-checked. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
