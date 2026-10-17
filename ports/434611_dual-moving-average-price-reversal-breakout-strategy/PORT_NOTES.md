# #434611 Dual Moving Average Price Reversal Breakout Strategy -> `fmz_434611_combo_123_displaced_envelope`

- FMZ source id: 434611 (lineage).
- Source: https://www.fmz.com/strategy/434611 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 18:15:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and a percent envelope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `pct` [0.5, 1.0]: **4 trials**; the 123 smoothing / D length / level, EMA 9 and displacement 13 fixed; `pct` sets both sides.

## Ambiguities resolved

- Contrarian envelope as written; na until the first break. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
