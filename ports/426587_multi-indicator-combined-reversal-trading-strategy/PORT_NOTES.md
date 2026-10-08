# #426587 Multi indicator Combined Reversal Trading Strategy -> `fmz_426587_combo_123_reversal_cmo_disparity`

- Source: https://www.fmz.com/strategy/426587 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-13 15:04:40). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [14, 21] x `len_second` [25, 20] x `len_third` [10, 5]: **8 trials**, defaults 14 / 25 / 10 (the source's); EMA 50, k 1, d 3, level 50 fixed.

## Ambiguities resolved

- CMOD: the -1 test (res10 > res50) comes first, as in the source.
- "Trade reverse" off.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
