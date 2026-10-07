# #363803 Super Scalper - 5 Min 15 Min -> `fmz_363803_super_scalper_wide_body`

- Source: https://www.fmz.com/strategy/363803 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-17 14:38:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [7, 14, 28] x `mult` [0.5, 1.0, 1.5] = **9 trials**. RSI 14 / 50 stays at the original.

## Ambiguities resolved

- stopLoss/takeProfit are computed but never passed to an order; EMA crosses only draw.
- `tr(true)`: the first bar's range is high - low.
- `FREQ = "1min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`none`
