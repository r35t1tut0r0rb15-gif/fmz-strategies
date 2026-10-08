# #426836 Bear Market MACD Short Strategy -> `fmz_426836_bear_macd_short`

- Source: https://www.fmz.com/strategy/426836 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 18:04:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`ema_len` [200, 450] x `stop_pct` [2, 4] x `target_pct` [8, 4]: **8 trials**, defaults 450 / 4 / 8 (the source's); MACD 11 / 26 / 9 fixed.

## Ambiguities resolved

- Stop / target from the signal bar's high / low, as fractions of its close applied to the fill.
- Start date dropped (backtest window).
- Short only; stops on 2h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`coarse_bar_stop`
