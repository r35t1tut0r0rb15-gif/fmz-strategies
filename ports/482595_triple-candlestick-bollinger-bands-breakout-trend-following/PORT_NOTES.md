# #482595 Triple Candlestick Bollinger Bands Breakout Trend Following Strategy with High Low Point Confirmation -> `fmz_482595_bb20_three_bar_band_walk_1r_bracket_flat_only`

- FMZ source id: 482595 (lineage).
- Source: https://www.fmz.com/strategy/482595 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 11:05:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; candle-sequence bracket as fractions of the fill |
| 2 | PASS | Three-bar band walks with a 1:1 bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; stop at the first bar, target 1 x risk.

## Ambiguities resolved

- Entries only from flat. FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
