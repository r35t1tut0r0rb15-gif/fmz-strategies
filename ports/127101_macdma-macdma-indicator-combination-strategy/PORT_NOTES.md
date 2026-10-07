# #127101 你不知道的MACDMA指标组合策略 -> `fmz_127101_macd_dual_sma_trend`

- Source: https://www.fmz.com/strategy/127101 (MyLanguage, author Zero, FMZ last modified
  2018-12-14 10:25:27). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model: all rules on completed bars. |
| 2 | ADAPT | 5 % stop -> `stop_atr` x ATR(14) of the entry signal bar. |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | No sizing in the code (one lot per signal); `SETSIGPRICETYPE` order-price lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ma_fast` [30, 50, 80] x `ma_slow` [100, 120, 200] x `stop_atr` [3, 6, 9] = **27 trials**.
MACD 12/26/9 fixed. `stop_atr` 6 is the declared stand-in for 5 % on 1 h bars (a wide
disaster stop); the grid brackets it.

## Ambiguities resolved

- The stop compares the bar's LOW (long) / HIGH (short) with the level, on the completed bar;
  the exit fills at the next open (not at the level).
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: the MA order and price-vs-MA conditions drive it; MACD is a filter.

## Marks (2026-10-07)

`none`
