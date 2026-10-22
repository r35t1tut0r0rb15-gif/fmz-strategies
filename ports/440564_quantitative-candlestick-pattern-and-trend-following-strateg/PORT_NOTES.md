# #440564 Quantitative Candlestick Pattern and Trend Following Strategy -> `fmz_440564_turtle_close_channel_long_short`

- FMZ source id: 440564 (lineage).
- Source: https://www.fmz.com/strategy/440564 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-31 17:24:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Closing-price channels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_fast` [20, 55] x `exit_fast` [10, 20]: **4 trials**; the short exit follows exit_fast.

## Ambiguities resolved

- Candle patterns plot only; date window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
