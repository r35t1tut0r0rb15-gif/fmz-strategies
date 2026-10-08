# #426460 Sell in May Buy in September Strategy -> `fmz_426460_sell_may_buy_september`

- Source: https://www.fmz.com/strategy/426460 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-12 11:18:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A21). Not run.

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

`buy_month` [9, 10, 11] x `sell_month` [5]: **3 trials**, defaults 9 / 5 (the source's).

## Ambiguities resolved

- Long only.
- `month` = month of the bar's broker day.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks (2026-10-07)

`none`
