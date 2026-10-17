# #488244 交叉突破型双均线系统策略-Cross-Breakout-Dual-EMA-System-Strategy -> `fmz_488244_ema32_hl_clean_candle_breakout`

- FMZ source id: 488244 (lineage).
- Source: https://www.fmz.com/strategy/488244 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 11:14:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs of highs and lows and candle colours. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [32, 50]: **2 trials**; default 32 (the source's). The source has no other input.

## Ambiguities resolved

- `ta.valuewhen(cross, bar_index, 0) > ta.valuewhen(clean candle, bar_index, 1)`: the first clean candle since the
  last cross (false until two clean candles exist).
- The script's in-trade flags gate entries; the Pine position follows the orders, with closes acting on the position
  at the bar's start (#430850). A short entry while long (only after the flags were cleared) reverses: REVERSAL
  INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_channel_breakout"`.

## Marks

`none`
