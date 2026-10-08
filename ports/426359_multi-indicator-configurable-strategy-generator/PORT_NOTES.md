# #426359 Multi Indicator Configurable Strategy Generator -> `fmz_426359_strategy_creator_confluence`

- Source: https://www.fmz.com/strategy/426359 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-11 14:33:12). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

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

`sl_pct` [0.4, 0.8] x `tp_pct` [0.5, 1.0] x `max_in_row` [1, 3]: **8 trials**, defaults 0.4 / 0.5 / 3 (the source's); indicator lengths and levels fixed at the source's defaults.

## Ambiguities resolved

- `strategy.closedtrades.size(k)` with k < 0 read as na (nz -> allowed), as with no closed trade.
- Stop / limit are fractions of the fill price; simulate() mirrors them because entries need a flat position, and records each closed trade's side for the 3-in-a-row filter.
- Test-period window (2023) dropped; unused inputs (MACD time frame, RSI MA, histogram averages) do not reach orders.
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
