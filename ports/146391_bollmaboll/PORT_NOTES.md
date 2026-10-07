# #146391 bollmaboll -> `fmz_146391_boll_band_ma_cross`

- Source: https://www.fmz.com/strategy/146391 (Python, author 3piggy, FMZ last modified
  2020-04-23 16:46:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar every 30 s; the port evaluates the same rule once per completed bar. |
| 2 | PASS | Bands, MAs and RSI thresholds are dimensionless. |
| 3 | PASS | Spot `exchange.Buy/Sell` only. |
| 4 | DONE | 10 % of balance / stocks per order, the unbounded position counter (adds) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The description says signals are "still being filtered"; not used either way. |

## Declared grid (criterion 5)

`bo` [20, 25, 30] x `ma` [8, 13, 21] x `ma2` [5, 7, 10] = **27 trials**. Band width 2 and the
RSI 12 / 60 / 40 filter fixed.

## Ambiguities resolved

- The opposite entry signal steps the counter toward zero, so on one unit it flattens rather
  than reverses; adds beyond one unit are sizing.
- `FREQ = "1min"`: the `period` argument's default `true` (= 1) selects `PERIOD_M1` in the code.
  No backtest header (listed in `no_bar_size.csv` with that note); the code's own request is
  the source's bar size, not a chosen one.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`: entries on the band crossing its own average with the band
widening; exits on narrowing.

## Marks (2026-10-07)

`none`
