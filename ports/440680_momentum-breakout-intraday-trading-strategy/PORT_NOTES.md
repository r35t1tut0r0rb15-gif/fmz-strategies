# #440680 Momentum Breakout Intraday Trading Strategy -> `fmz_440680_pivot_set_one_bar_trades`

- FMZ source id: 440680 (lineage).
- Source: https://www.fmz.com/strategy/440680 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 10:32:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit MACD levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [20, 25] x `cooldown` [10, 20]: **4 trials**; the other levels fixed.

## Ambiguities resolved

- One-bar trades as written; price-unit levels as fractions. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
