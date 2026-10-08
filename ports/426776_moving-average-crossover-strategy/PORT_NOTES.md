# #426776 Moving Average Crossover Strategy -> `fmz_426776_two_sma_crosses`

- Source: https://www.fmz.com/strategy/426776 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 14:55:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426335` (Jaccard 0.65-0.80) with #426335 (PORT_CANDIDATE); best Jaccard 0.706 with #426335. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_pair` [(5, 21), (10, 30)] x `short_pair` [(14, 28), (10, 30)]: **4 trials**, defaults 5 / 21 and 14 / 28 (the source's constants).

## Ambiguities resolved

- Both crosses on one bar: the later short stands.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
