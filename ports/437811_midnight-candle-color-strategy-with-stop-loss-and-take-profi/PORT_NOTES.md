# #437811 Midnight Candle Color Strategy with Stop Loss and Take Profit -> `fmz_437811_premidnight_candle_colour_bracket`

- FMZ source id: 437811 (lineage).
- Source: https://www.fmz.com/strategy/437811 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 16:37:35). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.57, 2.0] x `atr_len` [14, 50]: **4 trials**; the 05:00 / 06:00 UTC clock and the target ratios fixed.

## Ambiguities resolved

- Fixed UTC-5 clock without DST; tick bracket -> ATR multiples (reading and a wider stop); bracket re-placement not modelled. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
