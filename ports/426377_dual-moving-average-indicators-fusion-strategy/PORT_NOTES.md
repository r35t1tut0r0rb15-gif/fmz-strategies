# #426377 Dual Moving Average Indicators Fusion Strategy -> `fmz_426377_combo_2_20_ema_apo`

- Source: https://www.fmz.com/strategy/426377 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-11 16:32:22). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [14, 20] x `apo_long` [20, 30]: **4 trials**, defaults 14 / 20 (the source's), APO short 10 fixed.

## Ambiguities resolved

- First bar: nHH / nLL na, state keeps its previous value.
- "Trade reverse" off; start date (2005) dropped.
- FREQ = "12h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
