# #426925 Golden Cross Strategy -> `fmz_426925_golden_cross_long`

- Source: https://www.fmz.com/strategy/426925 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 15:50:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

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

`fast` [20, 50] x `slow` [100, 200]: **4 trials**, defaults 50 / 200 (the source's).

## Ambiguities resolved

- Long only (the crosses cannot coincide).
- FREQ = "2min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
