# #428577 RSI Trend Following Strategy -> `fmz_428577_pure_rsi_long`

- FMZ source id: 428577 (lineage).
- Source: https://www.fmz.com/strategy/428577 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:02:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [14, 7] x `rsi_top` [75, 80]: **4 trials**; defaults 14 / 75 (the source's); bands 30 / 55 / 60 / 70 fixed.

## Ambiguities resolved

- A same-bar close acts only on an open position. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
