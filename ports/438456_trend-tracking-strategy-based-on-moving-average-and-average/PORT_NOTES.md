# #438456 Trend Tracking Strategy Based on Moving Average and Average True Range -> `fmz_438456_noro_ma_atr_band_state`

- FMZ source id: 438456 (lineage).
- Source: https://www.fmz.com/strategy/438456 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 11:14:01). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA band of average true range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity lot, capital input and percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [30, 60] x `mult` [2.0, 1.0]: **4 trials**; ohlc4 source fixed.

## Ambiguities resolved

- Level-state entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
