# #489133 BTST高概率突破策略与精选股票筛选系统-BTST-High-Probability-Breakout-Strategy-with-Selective-Stock-Screening-System -> `fmz_489133_btst_1500_selection_long`

- FMZ source id: 489133 (lineage).
- Source: https://www.fmz.com/strategy/489133 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 09:33:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percentage changes and candle patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`change_lo` [2.0, 1.0]: **2 trials**; 2 % is the source's (the 3 % upper bound and the 15:00 bar fixed).

## Session open (check 9)

The selection is the hourly bar opening at 15:00 in the chart's time zone: UTC on the author's Binance chart, so
15:00 UTC here (no DST). "BTST" suggests an Indian 15:00 IST close, which no UTC-aligned hourly bar opens at;
decision owed if the IST reading is wanted.

## Ambiguities resolved

- The exit (close > a resistance reset to the current bar's high) can never fire: each long is held, as written.
- The "morning star" test is self-contradictory (never true), as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
