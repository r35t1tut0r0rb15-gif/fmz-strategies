# #440299 时空优化多时间框架MACD策略Time-and-Space-Optimized-Multi-Timeframe-MACD-Strategy -> `fmz_440299_macd_hist_three_candles_0900_bracket`

- FMZ source id: 440299 (lineage).
- Source: https://www.fmz.com/strategy/440299 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 10:15:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket from the close -> fixed fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.0003, 0.003] x `sl` [1.0, 0.01]: **4 trials**; MACD lengths and the window fixed.

## Ambiguities resolved

- Tick bracket as fixed fractions; window read on the UTC bar open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
