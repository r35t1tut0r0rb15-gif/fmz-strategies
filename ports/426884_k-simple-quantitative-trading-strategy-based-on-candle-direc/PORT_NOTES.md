# #426884 K Simple Quantitative Trading Strategy Based on Candle Direction -> `fmz_426884_bar_up_down`

- Source: https://www.fmz.com/strategy/426884 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 11:45:01). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

No parameters: **1 trial**, the source as written.

## Ambiguities resolved

- Start date dropped (backtest window); a doji keeps the position.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
