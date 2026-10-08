# #426886 EMA Trend Following Strategy Based on EMA Crossover -> `fmz_426886_hl2_ema_cross`

- Source: https://www.fmz.com/strategy/426886 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 11:51:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

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

`length` [10, 20, 30] x `ratio` [3, 5]: **6 trials**, defaults 20 / 3 (the source's).

## Ambiguities resolved

- Long Only off: shorts reverse; the long close never fires.
- Start year dropped (backtest window).
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
