# #442971 Multi Timeframe Trend Trading Strategy Based on Compressed Indicators -> `fmz_442971_boom_hunter_hull_vol_spike_bracket`

- FMZ source id: 442971 (lineage).
- Source: https://www.fmz.com/strategy/442971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 17:40:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | Roofing-filter quotients with a Hull trend and a volatility spike |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lp_period` [6, 10] x `swing_length` [20, 50]: **4 trials**; the second wave, the Hull and the R:R fixed.

## Ambiguities resolved

- Bracket from the signal bar, re-based on the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
