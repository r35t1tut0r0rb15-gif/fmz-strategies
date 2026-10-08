# #426581 Multi factor Quantitative Trading Strategy -> `fmz_426581_ema_ribbon_rsi_stoch_flat`

- Source: https://www.fmz.com/strategy/426581 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 14:46:59). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426561` (Jaccard 0.65-0.80) with #426561 (PORT_CANDIDATE); best Jaccard 0.689 with #426561. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emas` [(8, 13, 21, 34, 55), (5, 9, 13, 21, 34)]: **2 trials**, default the source's 8 / 13 / 21 / 34 / 55; RSI / stoch levels fixed.

## Ambiguities resolved

- Same rules as #426561 with the 8..55 ribbon (near-duplicate; possible_duplicates 0.69).
- Entries only from flat; exits only while in position.
- 2-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
