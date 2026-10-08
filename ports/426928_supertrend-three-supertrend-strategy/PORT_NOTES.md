# #426928 Supertrend Three Supertrend Strategy -> `fmz_426928_three_supertrends`

- Source: https://www.fmz.com/strategy/426928 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 15:59:15). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

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

`factor_scale` [0.75, 1.0, 1.5] (multiplies the factors 1.5 / 2 / 3): **3 trials**, default 1.0; ATR lengths 7 / 10 / 20 fixed.

## Ambiguities resolved

- Direction -1 is an up-trend; same-bar flips fill in source order, the last stands.
- close_all / cancel_all inputs off.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
