# #426367 Vegas Trend Wave Strategy -> `fmz_426367_vegas_wave`

- Source: https://www.fmz.com/strategy/426367 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 15:23:35). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`upd` [0.05, 0.1, 0.2] (one threshold for all three % gaps): **3 trials**, default 0.1 (the source's three equal inputs).

## Ambiguities resolved

- The short entry needs an open long (`position_size > 0`): from flat only longs open; kept as written.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
