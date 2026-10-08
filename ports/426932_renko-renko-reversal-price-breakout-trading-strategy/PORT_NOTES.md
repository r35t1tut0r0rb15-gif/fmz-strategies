# #426932 Renko Reversal Price Breakout Trading Strategy -> `fmz_426932_four_bar_reversal`

- Source: https://www.fmz.com/strategy/426932 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 16:27:29). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

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

`run` [3, 4, 5]: **3 trials**, default 4 (the source's).

## Ambiguities resolved

- Runs on ordinary candles despite the title; ported as coded.
- Qty 1 is sizing.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
