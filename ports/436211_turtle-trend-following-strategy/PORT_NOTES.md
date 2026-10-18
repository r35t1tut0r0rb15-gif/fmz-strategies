# #436211 Turtle trend Following Strategy -> `fmz_436211_turtle_counter_trend_pin_exits`

- FMZ source id: 436211 (lineage).
- Source: https://www.fmz.com/strategy/436211 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 11:41:30). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts and candle shapes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [50, 100] x `length3` [220, 100]: **4 trials**; EMA 15 fixed.

## Ambiguities resolved

- Breakout sides as written (counter-trend); orders in call order. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
