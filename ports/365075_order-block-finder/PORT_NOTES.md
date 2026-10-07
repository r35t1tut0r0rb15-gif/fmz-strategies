# #365075 Order Block Finder -> `fmz_365075_order_block_sequence`

- Source: https://www.fmz.com/strategy/365075 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-23 13:54:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`periods` [5, 7, 9] x `threshold` [0.0, 1.0] % = **6 trials**.

## Ambiguities resolved

- `security(res = "")` is the chart series; the threshold is a percent move (scale-free).
- The current bar is not part of the pattern, as coded.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
