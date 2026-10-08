# #426588 MACD RSI Trading Strategy for Oscillating Markets -> `fmz_426588_open_macd_rsi_range`

- Source: https://www.fmz.com/strategy/426588 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 15:14:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`over_sold` [55, 45] x `over_bought` [50, 60]: **4 trials**, defaults 55 / 50 (the source's); RSI 14, MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Re-read in A27: rejected in A23 for pyramiding 2 stacking, which SURVEY_README classes as sizing; the net position is ported.
- Indicators read the open, as written.
- Date window dropped. Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
