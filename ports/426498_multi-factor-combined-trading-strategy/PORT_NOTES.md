# #426498 Multi factor Combined Trading Strategy -> `fmz_426498_combo_123_reversal_bear_power`

- Source: https://www.fmz.com/strategy/426498 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 16:05:10). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426498` (Jaccard >= 0.80) with #432762 (DUPLICATE); best Jaccard 0.954 with #432762. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `length_bp` [13, 21]: **4 trials**, defaults 14 / 13 (the source's); k 1, d 3, level 50, trigger 0 fixed.

## Ambiguities resolved

- Daily bars: DayHigh is each bar's high.
- Trigger 0 is unit-free (kept).
- "Trade reverse" off.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
