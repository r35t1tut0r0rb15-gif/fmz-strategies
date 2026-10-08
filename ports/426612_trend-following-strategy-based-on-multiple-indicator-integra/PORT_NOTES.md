# #426612 Trend Following Strategy Based on Multiple Indicator Integration -> `fmz_426612_femi_macd_rsi_long`

- Source: https://www.fmz.com/strategy/426612 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 17:16:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

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

`rsi_len` [14, 21] x `over_sold` [30, 25] x `over_bought` [70, 75]: **8 trials**, defaults 14 / 30 / 70 (the source's); ADX, MACD and BB settings fixed.

## Ambiguities resolved

- No pyramiding: one long at a time; strategy.cancel only cancels unfilled orders.
- Same bar: from flat the entry stands; while long the entry is refused and a close goes flat.
- Long only (short entries commented out); Pine population stdev.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
