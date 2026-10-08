# #426844 Quantitative Strategy Based on Dual Exponential Moving Average -> `fmz_426844_ema_29_86_state`

- Source: https://www.fmz.com/strategy/426844 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 19:51:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

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

`small_ema` [20, 29] x `long_ema` [86, 120]: **4 trials**, defaults 29 / 86 (the source's).

## Ambiguities resolved

- strategy.entry reverses: REVERSAL INTENDED.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
