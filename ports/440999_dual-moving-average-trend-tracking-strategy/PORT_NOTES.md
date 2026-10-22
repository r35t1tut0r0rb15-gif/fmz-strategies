# #440999 Dual Moving Average Trend Tracking Strategy -> `fmz_440999_channel_trend_two_candle_pullback_reversal`

- FMZ source id: 440999 (lineage).
- Source: https://www.fmz.com/strategy/440999 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-04 15:57:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel trend, EMA filter and candle colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427189. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `bars` [2, 1]: **4 trials**; fast EMA 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
