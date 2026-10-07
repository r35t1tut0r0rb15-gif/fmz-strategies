# #365320 Consolidation Zones - Live -> `fmz_365320_consolidation_zone_breakout`

- Source: https://www.fmz.com/strategy/365320 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 11:43:02). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`prd` [5, 10, 20] x `conslen` [3, 5, 8] = **9 trials**.

## Ambiguities resolved

- `highestbars(10) == 0` read as high equal to the 10-bar high (ties to the current bar).
- The 1000-bar loop is the current dir run: pp = extreme swing value since dir changed; `change(pp)` false when either value is na.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
