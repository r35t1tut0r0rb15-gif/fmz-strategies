# #435514 Seven Candlestick Oscillation Breakthrough Strategy -> `fmz_435514_seven_candles_clock_close`

- FMZ source id: 435514 (lineage).
- Source: https://www.fmz.com/strategy/435514 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 16:14:32). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Clock-time closes in the exchange time zone (UTC) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [7, 5, 9]: **3 trials**; the four clock closes fixed.

## Ambiguities resolved

- Clock closes in UTC; close wins on a close bar. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
