# #430069 Dual Bandpass Filter Strategy -> `fmz_430069_bandpass_filter_zones`

- FMZ source id: 430069 (lineage).
- Source: https://www.fmz.com/strategy/430069 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-24 17:00:02). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit zones -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430069. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `zone_atr` [0.1, 0.5]: **4 trials**; delta 0.5 and ATR 14 fixed.

## Ambiguities resolved

- Zones +-5 (price units) -> +-zone_atr x ATR(14). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
