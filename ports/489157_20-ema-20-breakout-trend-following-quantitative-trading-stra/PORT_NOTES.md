# #489157 20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-Quantitative-Trading-Strategy -> `fmz_489157_close_ema20_cross_long`

- FMZ source id: 489157 (lineage).
- Source: https://www.fmz.com/strategy/489157 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:31:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An EMA only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50]: **2 trials**; 20 is the source's.

## Ambiguities resolved

- The win-rate counters only feed a label. Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
