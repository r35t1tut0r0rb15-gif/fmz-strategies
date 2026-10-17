# #433403 Price Reversal Strategy Guided by Price Channel -> `fmz_433403_noro_price_channel_pullback`

- FMZ source id: 433403 (lineage).
- Source: https://www.fmz.com/strategy/433403 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-27 11:40:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel position, candle colour and body ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slowlen` [30, 60] x `pcbars` [1, 3]: **4 trials**; the body filter (1/5 of SMA 10) fixed.

## Ambiguities resolved

- Channel of closes including the current bar. REVERSAL INTENDED. FREQ = "1min" (the title's D1 is not used).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
