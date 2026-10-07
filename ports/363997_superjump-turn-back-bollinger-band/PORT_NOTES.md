# #363997 SuperJump Turn Back Bollinger Band -> `fmz_363997_bollinger_turn_back`

- Source: https://www.fmz.com/strategy/363997 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-18 11:27:17). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

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

`length` [20, 40, 68] x `mult` [1.5, 2.0, 2.5] = **9 trials**.

## Ambiguities resolved

- Bands on open (source default); population stdev.
- Wide band and ATR stop only feed alerts/plots.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
