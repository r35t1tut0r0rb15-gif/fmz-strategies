# #426363 HMA and CCI Combo Trend Following Strategy -> `fmz_426363_hma_cci_trend`

- Source: https://www.fmz.com/strategy/426363 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 15:02:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`hma_len` [14, 21, 34] x `cci_len` [10, 20]: **6 trials**, defaults 21 / 10 (the source's); CCI levels fixed.

## Ambiguities resolved

- v3 integer division: `hmaLen / 2` = 10.
- Exits test the position held at the bar close; close_all fills after the bar's entry order (an ignored same-side entry plus an exit ends flat).
- hmaExit off; RCI and leverage unused; date window dropped.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
