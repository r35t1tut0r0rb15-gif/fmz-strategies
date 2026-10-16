# #428103 Dual EMA with RSI Trend Following Strategy -> `fmz_428103_macd_turn_rsi`

- FMZ source id: 428103 (lineage).
- Source: https://www.fmz.com/strategy/428103 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-28 16:17:53). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_threshold` [0.2, 0.1] x `len` [7, 14]: **4 trials**; defaults 0.2 / 7 (the source's); EMA 8 / 24 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
