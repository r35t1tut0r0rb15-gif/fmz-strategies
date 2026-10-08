# #426904 Multi factor Reversal Tracking Strategy -> `fmz_426904_combo_123_reversal_re_rsi`

- Source: https://www.fmz.com/strategy/426904 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-12-01 14:59:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [14, 21] x `value` [50, 70] x `wild_per` [14, 21]: **8 trials**, defaults 14 / 50 / 14 (the source's).

## Ambiguities resolved

- Averages start from 1 (nz(..., 1)); the first bar counts as a loss bar (close[1] na).
- "Trade reverse" off.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
