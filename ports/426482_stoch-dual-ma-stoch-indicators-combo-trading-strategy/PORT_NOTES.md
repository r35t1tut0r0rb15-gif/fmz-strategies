# #426482 Stoch Dual MA Stoch Indicators Combo Trading Strategy -> `fmz_426482_ma_stoch_combo`

- Source: https://www.fmz.com/strategy/426482 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 14:44:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

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

`l_ma` [50, 100] x `l_ema` [25, 50] x `stk_long` [50, 60]: **8 trials**, defaults 50 / 25 / 50 (the source's); stoch 20 / 2 / 2 and short level 80 fixed.

## Ambiguities resolved

- InTime hard-coded true; the flag variables only colour.
- Both entries on one bar (possible while the MAs cross): both fill at the next open in source order, so the later short stands.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`none`
