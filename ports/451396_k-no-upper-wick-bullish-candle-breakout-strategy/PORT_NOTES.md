# #451396 无上引线看涨K线突破策略-No-Upper-Wick-Bullish-Candle-Breakout-Strategy -> `fmz_451396_no_upper_wick_green_bar_prev_low_exit_long`

- FMZ source id: 451396 (lineage).
- Source: https://www.fmz.com/strategy/451396 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 16:11:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Strong green candles with a previous-low exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wick_pct` [5.0, 10.0]: **2 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
