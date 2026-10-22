# #477529 Multi Period Trend Linear Engulfing Pattern Quantitative Trading Strategy -> `fmz_477529_bullish_engulfing_hold17_long`

- FMZ source id: 477529 (lineage).
- Source: https://www.fmz.com/strategy/477529 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 11:42:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Engulfing candles with a fixed holding time |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold_periods` [17, 8, 34]: **3 trials**.

## Ambiguities resolved

- Defaults ported (bullish engulfing, long). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
