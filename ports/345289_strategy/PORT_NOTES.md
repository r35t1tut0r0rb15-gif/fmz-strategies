# #345289 跨时间周期策略 -> `fmz_345289_ma_trend_rsi_dip_long`

- Source: https://www.fmz.com/strategy/345289 (JavaScript, author 一刀, FMZ last modified
  2022-02-15 09:37:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; the port evaluates on completed bars. |
| 2 | PASS | MA order and RSI thresholds. |
| 3 | PASS | Spot only. |
| 4 | DONE | All-cash buy, sell all, `splide_price`, order cancelling, 0.1 minimum -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author as #345036 (different filter). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`fast_ma` [5, 10] x `slow_ma` [20, 40] x `rsi_period` [5, 10] = **8 trials** (10 is the backtest
header's RSI period).

## Ambiguities resolved

- The name says "cross-timeframe" but the code reads one timeframe (15 min). Ported as coded.
- `FREQ = "15min"` from `GetRecords(PERIOD_M15)`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"` (as #128249).

## Marks (2026-10-07)

`none`
