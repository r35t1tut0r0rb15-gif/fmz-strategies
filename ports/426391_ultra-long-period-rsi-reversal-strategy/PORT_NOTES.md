# #426391 Ultra Long Period RSI Reversal Strategy -> `fmz_426391_rsi65_reversal`

- Source: https://www.fmz.com/strategy/426391 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 17:36:19). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A21). Not run.

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

`length` [30, 65, 100] x `band` [10, 15] (levels 50 -+ band): **6 trials**, defaults 65 / 10 (the source's 40 / 60).

## Ambiguities resolved

- strategy.entry reverses: REVERSAL INTENDED.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
