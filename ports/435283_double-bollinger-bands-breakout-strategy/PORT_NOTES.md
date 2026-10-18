# #435283 Double Bollinger Bands Breakout Strategy -> `fmz_435283_double_bb_breakout_long`

- FMZ source id: 435283 (lineage).
- Source: https://www.fmz.com/strategy/435283 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 17:33:24). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Bands and an ATR trailing level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `atr_len` [14, 21]: **4 trials**; Bollinger 20 fixed.

## Ambiguities resolved

- Close-based level and rally exits; exit-and-entry on one bar held through. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
