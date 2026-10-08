# #426991 Hull Moving Average Trend Following Strategy -> `fmz_426991_two_ema_directions`

- Source: https://www.fmz.com/strategy/426991 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-16 18:41:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426991` (Jaccard 0.65-0.80) with #430011 (PORT_CANDIDATE); best Jaccard 0.680 with #430011. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len0` [8, 13] x `len02` [21, 34]: **4 trials**, defaults 13 / 21 (the source's).

## Ambiguities resolved

- rising(x, 2) = x above both previous values. Hull MA, S/R and the 720-minute security values only plot.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
