# #427261 Quantitative Trading Strategy Based on High-Low Point Moving Averages -> `fmz_427261_hilo_sma_reversal`

- FMZ source id: 427261 (lineage).
- Source: https://www.fmz.com/strategy/427261 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 15:53:55). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [4, 8, 16] x `displace` [0, 1]: **6 trials**; defaults 4 / 0 (the source's).

## Ambiguities resolved

- testPeriod() is defined but never used by the orders: no date filter.
- Same-bar long and short conditions cannot both hold unless the bar's close is above the high average and below the low average (impossible while highs >= lows). REVERSAL INTENDED.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks

`none`
