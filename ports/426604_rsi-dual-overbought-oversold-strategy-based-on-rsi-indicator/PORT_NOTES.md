# #426604 RSI Dual Overbought Oversold Strategy Based on RSI Indicator -> `fmz_426604_rsi5_contrarian_target`

- Source: https://www.fmz.com/strategy/426604 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 16:58:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

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

`rsi_len` [5, 7] x `upper` [70, 80] x `tp_pct` [1.3, 3.0]: **8 trials**, defaults 5 / 80 / 1.3 (the source's).

## Ambiguities resolved

- Target re-issued every bar at 1.3 % of the current close (a moving level): trailing_stop_pending; the port fixes it at 1.3 % of the fill price.
- Stochastic RSI only plots; entries do not depend on the position (same-side signals while held are ignored by Pine and the engine alike), so no mirroring.
- 4-day bars from broker days in fixed blocks from 1970-01-01 (decision owed); target on 4-day bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`trailing_stop_pending, coarse_bar_stop`
