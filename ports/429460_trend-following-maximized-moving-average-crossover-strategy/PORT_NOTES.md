# #429460 Trend Following Maximized Moving Average Crossover Strategy -> `fmz_429460_sma9_50_cross_rsi_long`

- FMZ source id: 429460 (lineage).
- Source: https://www.fmz.com/strategy/429460 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 13:05:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses and an RSI level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 30 % of equity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429460. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`inshort` [9, 20] x `rsi_signal` [55, 50]: **4 trials**; SMA 50 and RSI 14 fixed.

## Ambiguities resolved

- Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
