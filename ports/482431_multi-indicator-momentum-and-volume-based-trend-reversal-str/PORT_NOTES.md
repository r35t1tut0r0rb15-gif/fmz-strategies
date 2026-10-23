# #482431 Multi Indicator Momentum and Volume Based Trend Reversal Strategy -> `fmz_482431_macd_cross_rsi_range_band_extreme_volume_1h_reversal`

- FMZ source id: 482431 (lineage).
- Source: https://www.fmz.com/strategy/482431 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:04:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings at range-band extremes with RSI and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_mult` [3.0, 2.0] x `rsi_lo` [40.0, 30.0]: **4 trials**; MACD 12 / 26 / 9, RSI 14 / 80, range 100.

## Ambiguities resolved

- Rare two-sided extremes. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
