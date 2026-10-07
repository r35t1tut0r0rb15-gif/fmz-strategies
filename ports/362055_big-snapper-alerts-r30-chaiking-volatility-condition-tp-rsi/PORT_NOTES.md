# #362055 Big-Snapper-Alerts-R30-Chaiking-Volatility-condition-TP-RSI -> `fmz_362055_snapper_supertrend_chaikin_rsi`

- Source: https://www.fmz.com/strategy/362055 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 21:37:30). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close state machine, market orders. |
| 2 | PASS | ATR bands, % ROC, RSI levels, bar-range stop. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code beyond defaults. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG362055` (Jaccard >= 0.80) with #441066 (DUPLICATE); best Jaccard 0.981 with #441066. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_factor` [2.5, 3.618] x `st_len` [5, 10] x `len_coloured` [12, 18, 24] = **12 trials**. Other settings at the source defaults.

## Ambiguities resolved

- Only the default signal filter ('SuperTrend') is ported; the other ten filter options are inputs.
- The close-based stop exists only on the long side (SLdown is never tested), as written.
- Exit and fresh entry on one bar: the close acts on the position held at the bar's start, the new entry re-opens.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
