# #429495 Relative Volume Trend Following Trading Strategy -> `fmz_429495_relative_volume_up_bar_calm_atr_trailing_line_long`

- FMZ source id: 429495 (lineage).
- Source: https://www.fmz.com/strategy/429495 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 16:19:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based trailing line |
| 2 | PASS | Relative-volume up bars in calm markets with an ATR trailing exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 20] x `vol_len` [5, 10]: **4 trials**; BB 20 / 2.

## Ambiguities resolved

- Trailing line as written (reset to 0 while flat). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_breakout"`.

## Marks

`none`
