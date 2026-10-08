# #410112 分享RSI超买超卖策略 -> `fmz_410112_rsi_30_70_long_only`

- Source: https://www.fmz.com/strategy/410112 (Python, author 盯盘狗 - 策略出租, FMZ last
  modified 2023-04-18 12:46:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; evaluated on completed bars. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Spot pair in the code only (symbol string). |
| 4 | DONE | Order-size lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [7, 14, 21] x `rsi_buy` [25, 30] x `rsi_sell` [70, 75] = **12 trials**.

## Ambiguities resolved

- Polls the forming bar every 60 s; the port evaluates completed bars (as #345289).
- Spot, long only, as written; talib.RSI is Wilder's.
- `FREQ = "1min"` from the code (`period = '1m'`).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
