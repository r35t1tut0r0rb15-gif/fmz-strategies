# #434708 Quantitative Trading Based on Moving Average Envelope and ATR Trailing Stop -> `fmz_434708_made_atr_trail_filter`

- FMZ source id: 434708 (lineage).
- Source: https://www.fmz.com/strategy/434708 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 15:53:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A percent envelope and an ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pct` [0.5, 1.0] x `atr_mult` [2.0, 3.0]: **4 trials**; EMA 9, displacement 13 and ATR 15 fixed; `pct` sets both sides.

## Ambiguities resolved

- Same-side closes only, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks

`none`
