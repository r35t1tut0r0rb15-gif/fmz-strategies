# #442545 Adaptive Fluctuation Strategy Based on Quantitative Range Breakthrough -> `fmz_442545_volume_range_high_heikin_ashi_direction_1h_reversal`

- FMZ source id: 442545 (lineage).
- Source: https://www.fmz.com/strategy/442545 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 16:50:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-range breakouts in the Heikin-Ashi candle's direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_len` [5, 10]: **2 trials**; Heikin-Ashi on.

## Ambiguities resolved

- HA candles of the chart's own bars. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
