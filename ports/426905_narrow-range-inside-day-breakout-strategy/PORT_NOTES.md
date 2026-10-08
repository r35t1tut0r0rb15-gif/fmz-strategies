# #426905 Narrow Range Inside Day Breakout Strategy -> `fmz_426905_nr7_inside_day_long`

- Source: https://www.fmz.com/strategy/426905 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-12-01 15:00:06). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

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

`nr_bars` [4, 7] x `ma_length` [14, 28]: **4 trials**, defaults 7 / 14 (the source's).

## Ambiguities resolved

- The entry bar is green; its close finds no position, so the long stands until the next green bar.
- Long only.
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
