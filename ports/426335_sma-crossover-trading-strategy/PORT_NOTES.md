# #426335 SMA Crossover Trading Strategy -> `fmz_426335_sma_4_34_cross`

- Source: https://www.fmz.com/strategy/426335 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 11:42:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426335` (Jaccard 0.65-0.80) with #426776 (PORT_CANDIDATE); best Jaccard 0.706 with #426776. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [4, 8] x `slow` [34, 55]: **4 trials**, defaults 4 / 34 (the source's constants).

## Ambiguities resolved

- The short check comes first in the source (cannot coincide with the long one).
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
